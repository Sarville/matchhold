#!/home/user/.venvs/stable-audio/bin/python
"""Генерация SFX через Stable Audio Open Small -> www/audio/<name>.{ogg,mp3}.

Запуск: rebranding/tools/gen_sfx.py [--only click,roar] [--seed 0] [--out DIR]
Длина и громкость берутся у оригиналов из rebranding/archive/audio-original.
"""
import argparse, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf, torch
from einops import rearrange
from stable_audio_tools.models.pretrained import get_pretrained_model
from stable_audio_tools.inference.generation import generate_diffusion_cond

ROOT = Path(__file__).resolve().parents[2]
ORIG = ROOT / "rebranding/archive/audio-original"
STYLE = "fantasy game sound effect, medieval, clean, no music, no voice"

# имя файла -> промпт
P = {
    "click": "soft wooden button click, small UI tap",
    "tileclick": "tiny dry tick of a clay tile tapped, very short",
    "match-test": "two clay tiles matching, short bright wooden chime pop",
    "blunt": "dull muffled fist punch thud, soft heavy thump on leather, no ring",
    "monsterhit": "monster claw swipe striking leather armor, meaty heavy whump with a rough scrape, low",
    "arrowhit": "arrow thudding into a wooden target, short dull muffled thunk",
    "bite": "dragon bite, dull heavy chomp, muffled jaws snapping shut with a low crunch",
    "slash": "sword strike on armor, loud metallic clang, sharp steel clash with bright ringing overtone",
    "blockup": "wooden shield raised, short muffled clunk",
    "blockdown": "wooden building block dropped onto stone, clear solid knock with a bright clay clink, distinct",
    "shieldhit": "club hitting a wooden shield, bright hollow wooden knock with a slight ringing clank, crisp",
    "die": "small monster defeated, short wet groan and puff of dust",
    "shoot": "bow string twang and arrow whoosh, short",
    "open": "wooden chest latch click and short creak",
    "heal": "gentle warm magical healing chime, soft sparkle, harp glissando",
    "bomb": "black powder bomb explosion, short blast with rumble",
    "equip": "leather and chainmail armor equip rustle with small metal clink",
    "teleport": "magical teleport warp, airy rising whoosh with sparkle",
    "tilexplode": "clay tile shattering into pieces, short crunchy crack",
    "wing": "big dragon wing flap, leathery whoosh of air",
    "haste": "fast magical wind swoosh rising in pitch, speed buff",
    "reset": "wooden tiles shuffling and clattering on a table with a whoosh",
    "phasechange": "deep boss drum hit with ominous low rumble and rising tension",
    "freeze": "time freeze spell, crystalline icy shimmer with glassy chimes fading slowly",
    "levelup": "short triumphant fantasy fanfare, bright harp and bell arpeggio going up",
    "land": "giant dragon landing, heavy ground impact thud with rumbling tremor",
    "roar": "huge dragon roar, deep growling beast, powerful",
    "dshoot": "dragon spitting a fireball, quick fiery whoosh",
    "fireexplode": "fireball explosion burst, short crackling boom",
    "charge": "dragon charging fire breath, building roaring flame energy rising",
    "ice": "ice cracking and shattering, sharp glassy crystal break",
    "fire": "torch flames whoosh with crackling embers",
    "dexplode": "armored dragon segment exploding, bone and stone crack with fire boom",
    "dannihilate": "giant dragon final death, massive explosion with long rumble and falling debris",
    "lichspell": "dark necromancer spell, eerie ghostly whisper with low magical pulse",
}


# имя -> (длительность, +дБ к громкости оригинала); для новых без оригинала — (длительность, абсолютные дБ)
TUNE = {"blockdown": (0.30, 8), "slash": (0.40, 4), "blunt": (0.20, 4)}
NEW = {"shieldhit": (0.30, -17.0), "arrowhit": (0.20, -19.0), "bite": (0.35, -17.0), "monsterhit": (0.30, -18.0)}
LOWPASS = {"monsterhit": 3500, "blunt": 2500, "arrowhit": 2500, "bite": 3000}  # Гц: глухие звуки


def probe(name):
    if name in NEW:
        return NEW[name][0], NEW[name][1], -1.5
    f = ORIG / f"{name}.ogg"
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
    vd = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    mean_db = float(re.search(r"mean_volume: (-?[\d.]+) dB", vd).group(1))
    if name in TUNE:
        dur, mean_db = TUNE[name][0], mean_db + TUNE[name][1]
    return dur, mean_db, -1.5  # потолок пика


BRIGHT = {"slash", "shieldhit", "blockdown"}


def centroid(x, sr):
    m = np.abs(np.fft.rfft(x))
    return float(np.dot(np.fft.rfftfreq(len(x), 1 / sr), m) / (m.sum() + 1e-9))


def rms(x):
    return np.sqrt(np.dot(x, x) / len(x))  # не (x**2).mean(): numpy 1.26 + py3.14 портит x на месте


def process(x, sr, dur, mean_db, peak_db, lowpass=None):
    x = x.mean(0)
    if lowpass:
        f = np.fft.rfft(x)
        f[np.fft.rfftfreq(len(x), 1 / sr) > lowpass] = 0
        x = np.fft.irfft(f, len(x))
    keep = np.flatnonzero(np.abs(x) > 0.02 * np.abs(x).max())
    x = x[keep[0]:] if len(keep) else x  # ponytail: срез тишины в начале
    n = int(dur * sr)
    x = np.pad(x, (0, max(0, n - len(x))))[:n]
    fade = min(int(0.03 * sr), n // 4)
    x[-fade:] *= np.linspace(1, 0, fade)
    x = x * 10 ** (mean_db / 20) / rms(x)  # выравнивание по среднему уровню оригинала
    x = (x * min(1.0, 10 ** (peak_db / 20) / np.abs(x).max())).astype(np.float64)  # потолок пика
    return x, abs(20 * np.log10(rms(x) + 1e-9) - mean_db)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--only", default="")
    a.add_argument("--seed", type=int, default=0)
    a.add_argument("--tries", type=int, default=6, help="сидов на звук; берётся ближайший по громкости к оригиналу")
    a.add_argument("--steps", type=int, default=8)
    a.add_argument("--out", default=str(ROOT / "www/audio"))
    a = a.parse_args()
    names = [n for n in a.only.split(",") if n] or list(P)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    model, cfg = get_pretrained_model("stabilityai/stable-audio-open-small")
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(dev)
    sr = cfg["sample_rate"]

    for n in names:
        dur, mean_db, peak_db = probe(n)
        best = None
        for t in range(a.tries):
            audio = generate_diffusion_cond(
                model, steps=a.steps, cfg_scale=1.0,
                conditioning=[{"prompt": f"{P[n]}, {STYLE}", "seconds_total": max(dur + 0.5, 1.0)}],
                sample_size=cfg["sample_size"], sample_rate=sr, sampler_type="pingpong",
                seed=a.seed + t, device=dev)
            c, err = process(rearrange(audio, "b d n -> d (b n)").float().cpu().numpy(), sr, dur, mean_db, peak_db, LOWPASS.get(n))
            if n in BRIGHT:
                err -= 2 * np.log2(centroid(c, sr) / 1000)  # звонче = выше центроид, 1 октава ~ 2 дБ допуска
            if best is None or err < best[0]:
                best = (err, c)
        x = best[1]
        wav = out / f"{n}.wav"
        sf.write(wav, x, sr)
        for codec, ext in (("libvorbis", "ogg"), ("libmp3lame", "mp3")):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", codec, "-q:a", "5" if ext == "ogg" else "4", out / f"{n}.{ext}"], check=True)
        wav.unlink()
        print(f"{n}: {dur:.2f}s mean {mean_db:.1f} dB centroid {centroid(x, sr):.0f} Hz", flush=True)


if __name__ == "__main__":
    sys.exit(main())

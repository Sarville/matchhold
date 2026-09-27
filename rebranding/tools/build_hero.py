"""Сборка спрайт-листа героя из полос 2x2 (out/anim/hero/hero_<id>_v<N>.png) -> out/anim/hero/hero_sheet.png (+ превью).
Запуск из rebranding/: python3 tools/build_hero.py [--webp]   (--webp: ещё и ../www/img/v2/hero.webp)
Ячейка 64x56 логических px, x3 (192x168); 13 рядов как в старом monsters.png (ряды 2, 4, 6, 12 = зеркало).
Масштаб общий: стоящий герой (idle) = HERO_H логических px. Привязка: низ ограничивающего прямоугольника = низ ячейки,
по x центр нижних 45% фигуры (ступни стоят на месте, выпад и меч выходят вперёд).
ponytail: единый масштаб на все полосы; если модель раздула/сжала персонажа в полосе, поправить SCALE_ADJ[id]."""
import glob, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

A = "out/anim/hero/"; CACHE = "/tmp/mm_keyed/"; os.makedirs(CACHE, exist_ok=True)
X = 3; CW, CH = 64 * X, 56 * X; HERO_H = 36 * X; PAD = 1 * X
# ряд: (id полосы, кадры отзеркалить в ряд+1)
ROWS = {0: "idle", 1: "walk", 3: "attack_sword", 5: "die", 7: "emerge", 8: "build", 9: "carry_walk", 10: "loot", 11: "attack_fist"}
MIRROR = {1: 2, 3: 4, 5: 6, 11: 12}
SCALE_ADJ = {}          # id -> множитель поверх общего масштаба
SHIFT_X = {}            # id -> сдвиг по x (логические px x3), если полоса ушла в сторону

def latest(i):
    fs = sorted(glob.glob(f"{A}hero_{i}_v*.png"), key=lambda f: int(re.search(r"_v(\d+)\.png", f).group(1)))
    return fs[-1] if fs else None

def keyed(p):
    out = CACHE + "hero_" + os.path.basename(p)
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(p):
        subprocess.run(["python3", "tools/key_layer.py", p, out], check=True)
    return Image.open(out).convert("RGBA")

def frames(i):
    im = keyed(latest(i)); w, h = im.size; cw, ch = w // 2, h // 2
    fr = [im.crop(((k % 2) * cw, (k // 2) * ch, (k % 2 + 1) * cw, (k // 2 + 1) * ch)) for k in range(4)]
    return [despeckle(f) for f in fr] if i.startswith("attack") else fr

def despeckle(f, frac=0.02):
    """убрать мелкие отдельные пятнышки (искры вокруг меча): компоненты < frac от самой большой"""
    from scipy import ndimage as ndi
    al = np.array(f.getchannel("A")); lab, n = ndi.label(al > 40)
    if n < 2: return f
    sz = ndi.sum(al > 40, lab, range(1, n + 1)); keep = [k + 1 for k, v in enumerate(sz) if v >= frac * sz.max()]
    al[~np.isin(lab, keep) & ndi.binary_dilation(al > 0, iterations=0)] = 0
    f = f.copy(); f.putalpha(Image.fromarray(al)); return f

def bbox(f, thr=40):
    a = np.array(f.getchannel("A")) > thr
    ys, xs = np.where(a); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1, a

def main():
    idle_h = np.mean([bbox(f)[3] - bbox(f)[1] for f in frames("idle")]); S = HERO_H / idle_h
    print("масштаб", round(S, 3), "idle h", round(idle_h))
    sheet = Image.new("RGBA", (4 * CW, 13 * CH), (0, 0, 0, 0)); prev = []
    for row, i in ROWS.items():
        if not latest(i): print("нет", i); continue
        fr = frames(i); s = S * SCALE_ADJ.get(i, 1)
        hs = [bbox(f)[3] - bbox(f)[1] for f in fr]; print(f"{i:13s} h кадров {hs} -> {[round(h * s / X, 1) for h in hs]} лог.px")
        for k, f in enumerate(fr):
            x0, y0, x1, y1, a = bbox(f); g = f.crop((x0, y0, x1, y1)); g = g.resize((max(1, round(g.width * s)), max(1, round(g.height * s))), Image.LANCZOS)
            lo = a[y0 + int((y1 - y0) * 0.55):y1, x0:x1]; ys, xs = np.where(lo); cx = (xs.mean() if len(xs) else (x1 - x0) / 2) * s
            px = round(CW / 2 - cx + SHIFT_X.get(i, 0)); py = CH - PAD - g.height
            big = Image.new("RGBA", (CW + 600, CH + 600), (0, 0, 0, 0)); big.alpha_composite(g, (px + 300, py + 300)); cell = big.crop((300, 300, 300 + CW, 300 + CH))
            if px < 0 or px + g.width > CW or py < 0: print(f"   ! {i} кадр {k} не влез: x {px}..{px + g.width} из {CW}, y {py}")
            sheet.alpha_composite(cell, (k * CW, row * CH))
            if row in MIRROR: sheet.alpha_composite(cell.transpose(Image.FLIP_LEFT_RIGHT), (k * CW, MIRROR[row] * CH))
    sheet.save(A + "hero_sheet.png"); print("лист", sheet.size)
    pv = Image.new("RGBA", sheet.size, (110, 130, 110, 255)); d = ImageDraw.Draw(pv)
    for r in range(14): d.line([(0, r * CH), (sheet.width, r * CH)], fill=(255, 255, 255, 60))
    for c in range(5): d.line([(c * CW, 0), (c * CW, sheet.height)], fill=(255, 255, 255, 60))
    pv.alpha_composite(sheet); pv.convert("RGB").save(A + "hero_sheet_preview.png")
    if "--webp" in sys.argv:
        sheet.save("../www/img/v2/hero.webp", "WEBP", lossless=False, quality=90, alpha_quality=95, method=6); print("webp", os.path.getsize("../www/img/v2/hero.webp") // 1024, "KB")

main()

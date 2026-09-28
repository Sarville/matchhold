"""Сборка спрайт-листа монстра из полос 2x2 (out/anim/monsters/<имя>/<имя>_<id>_v<N>.png) ->
out/anim/monsters/<имя>/<имя>_sheet.png (+превью). Обобщение tools/build_hero.py для отдельного файла на персонажа
(03-animation.md п.7.3: общий лист monsters.png при x3 был бы выше лимита текстуры телефона).
Запуск из rebranding/: python3 tools/build_monster.py <имя> <W_лог_px> <H_лог_px> <key_hex> [id ...]  (id по умолчанию: walk attack die)
Ряды: 0 walk, 1 walk-зеркало, 2 attack, 3 attack-зеркало, 4 die, 5 die-зеркало (+6/7 lich_spell при id=spell).
Ячейка прямоугольная (W и H отдельно, не квадрат из одной H) — иначе широких/низких (rat, spider) не влезает по x."""
import glob, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

NAME = sys.argv[1]; W = int(sys.argv[2]); H = int(sys.argv[3]); KEY = sys.argv[4]; IDS = sys.argv[5:] or ["walk", "attack", "die"]
A = f"out/anim/monsters/{NAME}/"; CACHE = "/tmp/mm_keyed/"; os.makedirs(CACHE, exist_ok=True)
X = 3; PAD = 1.8  # запас: замах/выпад атаки и разброс при смерти выходят за габарит стойки
CW, CH = round(W * PAD) * X, round(H * PAD) * X
HERO_H = H * X
ROWS = {"walk": 1, "attack": 3, "die": 5, "spell": 7}  # совпадает с рядами в живом коде игры (MOVE_ANIMS, attack.js, die.js, lichspell.js); ряд 0 = idle, монстрам не рисуем
MIRROR = {1: 2, 3: 4, 5: 6, 7: 8}

def latest(i):
    fs = sorted(glob.glob(f"{A}{NAME}_{i}_v*.png"), key=lambda f: int(re.search(r"_v(\d+)\.png", f).group(1)))
    return fs[-1] if fs else None

def keyed(p):
    out = CACHE + NAME + "_" + os.path.basename(p)
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(p):
        subprocess.run(["python3", "tools/key_layer.py", p, out, KEY], check=True)
    return Image.open(out).convert("RGBA")

def frames(i):
    im = keyed(latest(i)); w, h = im.size; cw, ch = w // 2, h // 2
    return [im.crop(((k % 2) * cw, (k // 2) * ch, (k % 2 + 1) * cw, (k // 2 + 1) * ch)) for k in range(4)]

def bbox(f, thr=40):
    a = np.array(f.getchannel("A")) > thr
    ys, xs = np.where(a); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1, a

def main():
    if not latest("walk"): print("нет walk-полосы, нужна для масштаба"); return
    walk_h = np.mean([bbox(f)[3] - bbox(f)[1] for f in frames("walk")]); S = HERO_H / walk_h
    print(NAME, "масштаб", round(S, 3), "walk h", round(walk_h))
    nrows = max(ROWS[i] for i in IDS if latest(i)) + 2
    sheet = Image.new("RGBA", (4 * CW, nrows * CH), (0, 0, 0, 0))
    for i in IDS:
        if not latest(i): print("нет", i); continue
        row = ROWS[i]; fr = frames(i)
        hs = [bbox(f)[3] - bbox(f)[1] for f in fr]; print(f"{i:8s} h кадров {hs} -> {[round(h * S / X, 1) for h in hs]} лог.px")
        for k, f in enumerate(fr):
            x0, y0, x1, y1, a = bbox(f); g = f.crop((x0, y0, x1, y1))
            g = g.resize((max(1, round(g.width * S)), max(1, round(g.height * S))), Image.LANCZOS)
            px = round((CW - g.width) / 2); py = CH - X - g.height
            big = Image.new("RGBA", (CW + 600, CH + 600), (0, 0, 0, 0)); big.alpha_composite(g, (px + 300, py + 300))
            cell = big.crop((300, 300, 300 + CW, 300 + CH))
            if px < 0 or px + g.width > CW or py < 0: print(f"   ! {i} кадр {k} не влез: x {px}..{px + g.width} из {CW}, y {py}")
            sheet.alpha_composite(cell, (k * CW, row * CH))
            if row in MIRROR: sheet.alpha_composite(cell.transpose(Image.FLIP_LEFT_RIGHT), (k * CW, MIRROR[row] * CH))
    sheet.save(A + f"{NAME}_sheet.png"); print("лист", sheet.size)
    pv = Image.new("RGBA", sheet.size, (110, 130, 110, 255)); d = ImageDraw.Draw(pv)
    for r in range(nrows + 1): d.line([(0, r * CH), (sheet.width, r * CH)], fill=(255, 255, 255, 60))
    for c in range(5): d.line([(c * CW, 0), (c * CW, sheet.height)], fill=(255, 255, 255, 60))
    pv.alpha_composite(sheet); pv.convert("RGB").save(A + f"{NAME}_sheet_preview.png")

main()

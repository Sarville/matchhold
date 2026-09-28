"""Сборка спрайтов дракона из out/anim/dragon/dragon_<id>_v<N>.png ->
out/anim/dragon/dragon_{body,head,neck}_sheet.png (+webp). Обобщение build_hero.py/build_monster.py,
03-animation.md п.6/7: тело — 5 рядов x 4 кадра, ряд+5 = зеркало (Dragon.ANIMATION_ROWS в dragon.js);
голова — 3 позы рта в ряд, ряд1 = зеркало (dragon.js animate(): y = flip? headHeight():0);
шея — 1 сегмент, ряд1 = зеркало (main.css .dragon.flip .neck background-position).
Запуск из rebranding/: python3 tools/build_dragon.py [--webp]"""
import glob, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

A = "out/anim/dragon/"; CACHE = "/tmp/mm_keyed/"; os.makedirs(CACHE, exist_ok=True)
X = 3
BODY_W, BODY_H = 204 * X, 164 * X; BODY_TARGET_H = 130 * X; PAD = 1 * X
HEAD_W, HEAD_H = 81 * X, 30 * X
NECK_W, NECK_H = 24 * X, 24 * X
ROWS = {0: "idle", 1: "fly", 2: "landing", 3: "windup", 4: "buffet"}

def latest(id_):
    fs = sorted(glob.glob(f"{A}dragon_{id_}_v*.png"), key=lambda f: int(re.search(r"_v(\d+)\.png", f).group(1)))
    return fs[-1] if fs else None

def keyed(p):
    out = CACHE + "dragon_" + os.path.basename(p)
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(p):
        subprocess.run(["python3", "tools/key_layer.py", p, out], check=True)
    return Image.open(out).convert("RGBA")

def frames_2x2(id_):
    im = keyed(latest(id_)); w, h = im.size; cw, ch = w // 2, h // 2
    return [im.crop(((k % 2) * cw, (k // 2) * ch, (k % 2 + 1) * cw, (k // 2 + 1) * ch)) for k in range(4)]

def frames_row(id_, n):
    im = keyed(latest(id_)); w, h = im.size; cw = w // n
    return [im.crop((k * cw, 0, (k + 1) * cw, h)) for k in range(n)]

def bbox(f, thr=40):
    a = np.array(f.getchannel("A")) > thr
    ys, xs = np.where(a); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1, a

def anchor_point(g):
    """Точка крепления шеи (плечо/грудь): альфа-центроид верхне-правой области КРОПНУТОГО кадра
    (правые 40%, верхние 55%) — эта зона стабильнее общего bbox между позами: не зависит от того,
    насколько широко раскинуты крылья или хвост (в отличие от центра масс всего силуэта).
    live-баг сессии 8: headMount/setNeckMount в игровом коде прибиты к одной точке ячейки,
    рассчитанной на то, что плечо всегда там же — раньше bbox-центровка каждого кадра независимо
    сдвигала плечо между позами, и голова-оверлей отрывалась от тела при атаках (WingBuffet и т.п.)."""
    a = np.array(g.getchannel("A")); w, h = g.size
    x0, y1 = int(w * 0.6), int(h * 0.55)
    region = a[0:y1, x0:w]
    ys, xs = np.where(region > 40)
    if len(xs) == 0:
        ys, xs = np.where(a > 40)
        return xs.mean(), ys.mean()
    return xs.mean() + x0, ys.mean()

def place(sheet, f, cx, cy, cw, ch, s, px_extra=0, anchor="bottom"):
    """f отмасштабирован на s, вписан в ячейку (cx,cy)..+cw,ch: bottom-anchor по низу и центру нижних 45% массы, либо center."""
    x0, y0, x1, y1, a = bbox(f)
    g = f.crop((x0, y0, x1, y1)); g = g.resize((max(1, round(g.width * s)), max(1, round(g.height * s))), Image.LANCZOS)
    if anchor == "bottom":
        lo = a[y0 + int((y1 - y0) * 0.55):y1, x0:x1]; ys, xs = np.where(lo)
        cxm = (xs.mean() if len(xs) else (x1 - x0) / 2) * s
        px = round(cw / 2 - cxm) + px_extra; py = ch - PAD - g.height
    else:
        px = round((cw - g.width) / 2); py = round((ch - g.height) / 2)
    big = Image.new("RGBA", (cw + 600, ch + 600), (0, 0, 0, 0)); big.alpha_composite(g, (px + 300, py + 300))
    sheet.alpha_composite(big.crop((300, 300, 300 + cw, 300 + ch)), (cx, cy))
    if px < 0 or px + g.width > cw or py < 0:
        print(f"   ! не влез: x {px}..{px + g.width} из {cw}, y {py}")

def place_anchor(sheet, f, cx, cy, cw, ch, s, target):
    """Как place(), но выравнивает НЕ bbox, а anchor_point(кадра) в фиксированную точку ячейки target=(ax,ay).
    Одна и та же target для всех кадров всех строк -> плечо/шея не гуляет между позами."""
    x0, y0, x1, y1, _ = bbox(f)
    g = f.crop((x0, y0, x1, y1))
    ax, ay = anchor_point(g)
    g = g.resize((max(1, round(g.width * s)), max(1, round(g.height * s))), Image.LANCZOS)
    px = round(target[0] - ax * s); py = round(target[1] - ay * s)
    big = Image.new("RGBA", (cw + 1200, ch + 1200), (0, 0, 0, 0)); big.alpha_composite(g, (px + 600, py + 600))
    sheet.alpha_composite(big.crop((600, 600, 600 + cw, 600 + ch)), (cx, cy))
    if px < 0 or px + g.width > cw or py < 0 or py + g.height > ch:
        print(f"   ! не влез: x {px}..{px + g.width} из {cw}, y {py}..{py + g.height} из {ch}")

def build_body():
    if not latest("idle"): print("нет idle, нужна для масштаба"); return
    print("тело: цель", BODY_TARGET_H, "px в листе (масштаб на ряд по медиане высоты кадров); плечо (anchor_point) выравнивается по единой точке для всех рядов/кадров")
    # Целевая точка плеча в ячейке = где anchor_point приземляется у idle-кадра0 старым способом
    # (bottom-anchor + центр нижних 45% массы) — эта поза уже подтверждена живьём (headMount по умолчанию совпадает).
    idle_fr = frames_2x2("idle")
    hs0 = [bbox(f)[3] - bbox(f)[1] for f in idle_fr]
    S0 = BODY_TARGET_H / np.median(hs0)
    calib = Image.new("RGBA", (BODY_W, BODY_H), (0, 0, 0, 0))
    place(calib, idle_fr[0], 0, 0, BODY_W, BODY_H, S0)
    x0, y0, x1, y1, _ = bbox(idle_fr[0])
    ax0, ay0 = anchor_point(idle_fr[0].crop((x0, y0, x1, y1)))
    # place() бросил старый (некалиброванный) кадр в клетку неким (px,py); чтобы узнать их, повторим его расчёт:
    a = np.array(idle_fr[0].getchannel("A")) > 40
    lo = a[y0 + int((y1 - y0) * 0.55):y1, x0:x1]; ys, xs = np.where(lo)
    cxm = (xs.mean() if len(xs) else (x1 - x0) / 2) * S0
    px0 = round(BODY_W / 2 - cxm); py0 = BODY_H - PAD - round((y1 - y0) * S0)
    target = (px0 + ax0 * S0, py0 + ay0 * S0)
    print("целевая точка плеча в ячейке:", [round(v) for v in target])

    sheet = Image.new("RGBA", (4 * BODY_W, 10 * BODY_H), (0, 0, 0, 0))
    for row, id_ in ROWS.items():
        if not latest(id_): print("нет", id_); continue
        fr = frames_2x2(id_)
        hs = [bbox(f)[3] - bbox(f)[1] for f in fr]
        S = BODY_TARGET_H / np.median(hs)
        print(f"{id_:8s} h кадров {[round(h) for h in hs]} масштаб {round(S, 3)} -> {[round(h * S / X, 1) for h in hs]} лог.px")
        for k, f in enumerate(fr):
            cell = Image.new("RGBA", (BODY_W, BODY_H), (0, 0, 0, 0))
            place_anchor(cell, f, 0, 0, BODY_W, BODY_H, S, target)
            sheet.alpha_composite(cell, (k * BODY_W, row * BODY_H))
            sheet.alpha_composite(cell.transpose(Image.FLIP_LEFT_RIGHT), (k * BODY_W, (row + 5) * BODY_H))
    sheet.save(A + "dragon_body_sheet.png"); print("тело лист", sheet.size)
    pv = Image.new("RGBA", sheet.size, (110, 130, 110, 255)); d = ImageDraw.Draw(pv)
    for r in range(11): d.line([(0, r * BODY_H), (sheet.width, r * BODY_H)], fill=(255, 255, 255, 60))
    for c in range(5): d.line([(c * BODY_W, 0), (c * BODY_W, sheet.height)], fill=(255, 255, 255, 60))
    pv.alpha_composite(sheet); pv.convert("RGB").save(A + "dragon_body_sheet_preview.png")
    return sheet

def build_head():
    if not latest("head"): print("нет head"); return
    fr = frames_row("head", 3)
    sheet = Image.new("RGBA", (3 * HEAD_W, 2 * HEAD_H), (0, 0, 0, 0))
    for k, f in enumerate(fr):
        x0, y0, x1, y1, _ = bbox(f); g = f.crop((x0, y0, x1, y1))
        s = min((HEAD_W - PAD) / g.width, (HEAD_H - PAD) / g.height)
        cell = Image.new("RGBA", (HEAD_W, HEAD_H), (0, 0, 0, 0))
        place(cell, f, 0, 0, HEAD_W, HEAD_H, s, anchor="center")
        sheet.alpha_composite(cell, (k * HEAD_W, 0))
        sheet.alpha_composite(cell.transpose(Image.FLIP_LEFT_RIGHT), (k * HEAD_W, HEAD_H))
    sheet.save(A + "dragon_head_sheet.png"); print("голова лист", sheet.size)
    return sheet

def build_neck():
    if not latest("neck"): print("нет neck"); return
    f = keyed(latest("neck"))
    x0, y0, x1, y1, _ = bbox(f); g = f.crop((x0, y0, x1, y1))
    s = min((NECK_W - PAD) / g.width, (NECK_H - PAD) / g.height)
    sheet = Image.new("RGBA", (NECK_W, 2 * NECK_H), (0, 0, 0, 0))
    cell = Image.new("RGBA", (NECK_W, NECK_H), (0, 0, 0, 0))
    place(cell, f, 0, 0, NECK_W, NECK_H, s, anchor="center")
    sheet.alpha_composite(cell, (0, 0))
    sheet.alpha_composite(cell.transpose(Image.FLIP_LEFT_RIGHT), (0, NECK_H))
    sheet.save(A + "dragon_neck_sheet.png"); print("шея лист", sheet.size)
    return sheet

def main():
    body = build_body(); head = build_head(); neck = build_neck()
    if "--webp" in sys.argv:
        for name, im in [("dragon", body), ("dragon_head", head), ("dragon_neck", neck)]:
            if im is None: continue
            im.save(f"../www/img/v2/{name}.webp", "WEBP", lossless=False, quality=90, alpha_quality=95, method=6)
            print("webp", name, os.path.getsize(f"../www/img/v2/{name}.webp") // 1024, "KB")

main()

"""Убирает заднюю стенку у павильона-хранилища (жилая линия), чтобы запас читался на фоне неба.
Запуск из rebranding/: python3 tools/open_pavilion.py  -> out/env/buildings/open/{shack_1,house_2,fort_3,castle_4}.png (+ mock_open.png)
Метод: цвет стенки берётся по центру проёма (store_layout.STAGES), связная область похожего цвета (по оттенку и насыщенности,
яркость свободна: швы досок темнее) внутри проёма расширяется до боковых стоек и закрывается морфологией."""
import os, sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

SRC = "out/env/buildings/composed/"; DST = "out/env/buildings/open/"; os.makedirs(DST, exist_ok=True)
# стадия: (центр x, ширина проёма, пол y, низ балки y) в px 960x1024, как в store_layout.py
ST = {"shack_1": (427, 285, 968, 715), "house_2": (432, 325, 925, 578), "fort_3": (425, 340, 895, 570), "castle_4": (427, 325, 895, 570)}

def rgb2hsv(a):
    import colorsys
    m = a.max(2); n = a.min(2); d = m - n
    h = np.zeros_like(m); s = np.where(m > 0, d / np.maximum(m, 1e-6), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    h = np.where(d == 0, 0, np.where(m == r, ((g - b) / np.maximum(d, 1e-6)) % 6, np.where(m == g, (b - r) / np.maximum(d, 1e-6) + 2, (r - g) / np.maximum(d, 1e-6) + 4))) / 6
    return h, s, m

def open_one(n, dbg=False):
    cx, w, fl, bm = ST[n]
    im = Image.open(SRC + n + ".png").convert("RGBA"); a = np.array(im).astype(float) / 255
    h, s, v = rgb2hsv(a[..., :3])
    y0, y1, x0, x1 = bm + 20, fl - 60, int(cx - w / 2 + 30), int(cx + w / 2 - 30)
    ref = np.median(a[y0:y1, x0:x1, :3].reshape(-1, 3), axis=0); rh, rs, rv = rgb2hsv(ref[None, None])
    rh, rs, rv = float(rh[0, 0]), float(rs[0, 0]), float(rv[0, 0])
    dh = np.minimum(abs(h - rh), 1 - abs(h - rh))
    wall = (a[..., 3] > 0.5) & (dh < 0.035) & (abs(s - rs) < 0.14) & (v < rv + 0.08) & (v > rv * 0.45)
    wall = ndi.binary_closing(wall, iterations=6); wall = ndi.binary_opening(wall, iterations=2)
    lab, nl = ndi.label(wall); seed = lab[(y0 + y1) // 2, cx]
    m = lab == seed if seed else np.zeros_like(wall)
    # обломки стенки внутри проёма (у стоек) тоже убираем: компоненты с центром в пределах проёма
    for i in range(1, nl + 1):
        if i == seed: continue
        ys, xs = np.where(lab == i)
        if len(ys) > 150 and cx - w / 2 - 20 <= xs.mean() <= cx + w / 2 + 20 and bm - 20 <= ys.mean() <= fl: m |= lab == i
    # ограничение: выше балки не режем (кровля/стропила), низ ограничен полом
    m[: bm - 30] = False; m[fl - 10:] = False
    # тёмная кромка стенки у стоек (тень): мягче критерий, но только внутри проёма между стойками
    relaxed = (a[..., 3] > 0.5) & (dh < 0.06) & (abs(s - rs) < 0.3) & (v < rv + 0.25) & (v > 0.12)
    rect = np.zeros_like(m); rect[bm - 10:fl - 12, int(cx - w / 2 + 16):int(cx + w / 2 - 16)] = True   # 16 px у стоек не трогаем (их тень похожа на стенку)
    extra = ndi.binary_opening(relaxed & rect, iterations=1)
    m |= extra & ndi.binary_dilation(m, iterations=45)
    m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=3))
    m[: bm - 30] = False; m[fl - 10:] = False
    return im, m

if __name__ == "__main__":
    tiles = []
    for n in ST:
        im, m = open_one(n)
        soft = Image.fromarray((ndi.binary_dilation(m, iterations=1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
        arr = np.array(im); al = np.array(im.getchannel("A")).astype(float) * (1 - np.array(soft) / 255)
        # плавающие обломки стенки (не связаны с телом) убираем
        lab, nl = ndi.label(al > 16, structure=np.ones((3, 3)))
        for i in range(1, nl + 1):
            sz = (lab == i).sum()
            if sz < 15000: al[lab == i] = 0
        arr[..., 3] = al.astype(np.uint8); out = Image.fromarray(arr); out.save(DST + n + ".png")
        bg = Image.new("RGBA", out.size, (140, 190, 240, 255)); bg.alpha_composite(out); tiles.append(bg.resize((480, 512)).convert("RGB"))
        print(n, "cut px:", int(m.sum()))
    sh = Image.new("RGB", (960, 1024)); [sh.paste(t, ((i % 2) * 480, (i // 2) * 512)) for i, t in enumerate(tiles)]; sh.save(DST + "mock_open.png")

"""Ключ #FF00FF -> альфа и приведение рамки к канонической геометрии (общей для дня и ночи).
Использование: fit_frame.py in.png out.png [IN0 IN1]
Внешний край 32..2015; проём по умолчанию 332..1715 (толщина 300), для тонкой рамки: fit_frame.py in out 182 1866 (толщина 150). Каждая ось переводится
кусочно-линейно: [внешний край..край проёма..край проёма..внешний край]."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUT0, OUT1, N = 32, 2016, 2048
IN0, IN1 = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (332, 1716)  # проём: по умолчанию толстая рамка, для тонкой 182 1866

im = np.array(Image.open(sys.argv[1]).convert("RGBA")).astype(float)
r, g, b, a0 = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
key = ((r > 190) & (b > 190) & (g < 90)) | (a0 < 10)
lab, n = ndi.label(key)
big = [i for i in range(1, n + 1) if (lab == i).sum() > 50000]
k = ndi.binary_dilation(np.isin(lab, big), iterations=1)  # ponytail: 1px erosion of key fringe; feather if halo shows
alpha = ndi.gaussian_filter((~k).astype(float), 0.7)
near = ndi.binary_dilation(k, iterations=3) & ~k
for c in (0, 2):  # despill: тянем розовое к зелёному у края
    ch = im[..., c]; ch[near] = np.minimum(ch[near], g[near] + 30); im[..., c] = ch
rgba = np.dstack([im[..., :3], alpha * 255]).clip(0, 255).astype(np.uint8)

solid = alpha > 0.5
oy, ox = np.where(solid)
inner = ndi.label(~solid)[0]; inner = inner == inner[N // 2, N // 2]
iy, ix = np.where(inner)
sx = (ox.min(), ix.min(), ix.max() + 1, ox.max() + 1)
sy = (oy.min(), iy.min(), iy.max() + 1, oy.max() + 1)
print("src outer", sx[0], sx[3], sy[0], sy[3], "opening", sx[1], sx[2], sy[1], sy[2])

def warp(img, src, axis):
    dst = (OUT0, IN0, IN1, OUT1)
    strips = []
    for i in range(3):
        box = [0, 0, img.size[0], img.size[1]]
        box[axis], box[axis + 2] = src[i], src[i + 1]
        size = [img.size[0], img.size[1]]
        size[axis] = dst[i + 1] - dst[i]
        strips.append(img.crop(tuple(box)).resize(tuple(size), Image.LANCZOS))
    return strips

img = Image.fromarray(rgba)
cols = warp(img, sx, 0)
canvas = Image.new("RGBA", (N, N), (0, 0, 0, 0))
# сначала по X на полной высоте исходника, потом по Y
tmp = Image.new("RGBA", (N, img.size[1]), (0, 0, 0, 0)); x = OUT0
for s in cols: tmp.paste(s, (x, 0)); x += s.size[0]
rows = warp(tmp, sy, 1); y = OUT0
for s in rows: canvas.paste(s, (0, y)); y += s.size[1]
canvas.save(sys.argv[2])

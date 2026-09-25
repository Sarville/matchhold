"""Ключ #FF00FF -> RGBA с мягким краем, без розовой каймы (для слоёв фона, переднего плана, лунок).
Использование: key_layer.py in.png out.png
Край: цвет берётся у ближайшего чистого пикселя, альфа = проекция пикселя на отрезок [цвет, #FF00FF]."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

M = np.array([255.0, 0.0, 255.0])
BAND = 10  # ширина каймы (px), ponytail: под боке шире 10 px поднять
a = np.array(Image.open(sys.argv[1]).convert("RGB")).astype(float)
d = np.linalg.norm(a - M, axis=2)
pink = np.minimum(a[..., 0], a[..., 2]) - a[..., 1]   # «розовость»: R и B выше G
clean = pink < 25                                 # цвет без примеси ключа
core = ndi.binary_erosion(clean, iterations=BAND)  # ядро: далеко от края, цвет без примеси
_, (iy, ix) = ndi.distance_transform_edt(~core, return_indices=True)
F = a[iy, ix]                                      # ближайший чистый цвет
v = F - M
t = np.einsum("ijk,ijk->ij", a - M, v) / np.maximum(np.einsum("ijk,ijk->ij", v, v), 1e-6)
alpha = np.clip(t, 0, 1)
alpha[core] = 1
alpha[d < 20] = 0                                  # чистый ключ
out = np.where(core[..., None], a, F)
Image.fromarray(np.dstack([out, alpha * 255]).clip(0, 255).astype(np.uint8)).save(sys.argv[2])

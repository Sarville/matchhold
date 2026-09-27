import numpy as np
from PIL import Image
from scipy import ndimage as ndi

def find_moon(path):
    im = np.array(Image.open(path).convert("RGB")).astype(float)
    H, W = im.shape[:2]
    lum = 0.299*im[...,0] + 0.587*im[...,1] + 0.114*im[...,2]
    region = np.zeros((H, W), bool); region[:int(H*0.5), :int(W*0.42)] = True
    core = (lum > 225) & region
    lab, n = ndi.label(core)
    if n == 0: return None
    sizes = ndi.sum(core, lab, range(1, n+1))
    best = np.argmax(sizes) + 1
    ys, xs = np.where(lab == best)
    cy, cx = ys.mean(), xs.mean()
    r = max(xs.max()-xs.min(), ys.max()-ys.min()) / 2
    return cx, cy, r, sizes.max()

for f in ["s1_far_night_land","s2_far_night_land","s3_far_night_land","s4_far_night_land","s1_far_night_port","s2_far_night_port","s3_far_night_port","s4_far_night_port"]:
    p = f"../www/img/v2/bg/{f}.webp"
    print(f, find_moon(p))

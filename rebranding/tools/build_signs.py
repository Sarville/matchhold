"""Столбики с табличками (день и ночь): ключ -> альфа, кроп по bbox, вписывание в холст 44x84 логических px (x12), низ = земля,
замер пластины под число (день: кремовая, ночь: тёмно-синяя) -> out/env/signs/signs.json (в логических px и px холста).
Запуск из rebranding/: python3 tools/build_signs.py. Одна и та же табличка слева (день + фаза) и справа (уровень); число и значок фазы рисует игра."""
import json, os, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

D = "out/env/signs/"
SEL = {"day": "sign_level_day_v2", "night": "sign_level_night_v1"}
K = 12; W, H = 44 * K, 84 * K   # 12 px на логический px

def plaque(a, night):
    r, g, b, al = [a[..., i].astype(int) for i in range(4)]; lum = r * .3 + g * .59 + b * .11
    m = ((al > 200) & (lum < 105) & (lum > 35) & (b > r + 12)) if night else ((al > 200) & (r > 215) & (g > 200) & (b > 165) & (r - b < 60))
    m = ndi.binary_opening(m, iterations=3); l, n = ndi.label(m)
    i = int(np.argmax(ndi.sum(m, l, range(1, n + 1)))) + 1; ys, xs = np.where(l == i)
    return [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]

if __name__ == "__main__":
    meta = {}; os.makedirs(D + "composed", exist_ok=True)
    for st, src in SEL.items():
        k = f"{D}keyed/{src}.png"
        if not os.path.exists(k): subprocess.run(["python3", "tools/key_layer.py", f"{D}{src}.png", k, "FF00FF"], check=True)
        im = Image.open(k).convert("RGBA"); im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox())
        r = min(W / im.width, H / im.height); im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
        c = Image.new("RGBA", (W, H)); c.alpha_composite(im, ((W - im.width) // 2, H - im.height)); c.save(f"{D}composed/sign_{st}.png")
        p = plaque(np.array(c), st == "night"); meta[st] = {"px": [W, H], "logical": [44, 84], "plaque_px": p, "plaque": [round(v / K, 1) for v in p]}
    a, b = meta["day"]["plaque"], meta["night"]["plaque"]; x0, y0 = max(a[0], b[0]), max(a[1], b[1])   # общая безопасная область числа (пластины дня и ночи чуть смещены)
    meta["safe"] = [x0, y0, round(min(a[0] + a[2], b[0] + b[2]) - x0, 1), round(min(a[1] + a[3], b[1] + b[3]) - y0, 1)]
    json.dump(meta, open(D + "signs.json", "w"), indent=1); print(json.dumps({s: (m["plaque"] if s != "safe" else m) for s, m in meta.items()}))

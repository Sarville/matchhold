"""Проверка: не совпадают ли ночные грани разных классов по цвету/оттенку.
Средний цвет по непрозрачным пикселям композитной грани (out/tiles/composed/night_*), в HSV.
Сравнение только между разными классами (внутри класса намеренная градация серии).
Запуск из rebranding/: python3 tools/audit_night_colors.py [порог_угла_hue, по умолчанию 18]"""
import colorsys
import glob
import itertools
import os
import sys

import numpy as np
from PIL import Image

HUE_THRESH = float(sys.argv[1]) if len(sys.argv) > 1 else 18.0

def blank_plate():
    plate = Image.open("out/tiles/keyed/plate_night_v2.png").convert("RGBA")
    box = plate.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    return np.array(plate.crop(box).resize((384, 384), Image.LANCZOS))[..., :3].astype(float)

BLANK = blank_plate()

def avg_hsv(path):
    """Доминирующий (не средний) оттенок там, где грань отличается от голой плашки (иконка+glow, без фона
    плашки): средний цвет смещает тонкое, но насыщенное glow-гало сильнее большого, но менее насыщенного
    тела иконки, а игрок видит именно тело. Мода по гистограмме hue (20 корзин), взвешенная по насыщенности."""
    im = np.array(Image.open(path).convert("RGBA").resize((384, 384), Image.LANCZOS))
    rgb = im[..., :3].astype(float)
    diff = np.linalg.norm(rgb - BLANK, axis=2)
    mask = diff > 90  # только заметно отличное от плашки: тело иконки + яркое ядро glow, без слабого дальнего гало
    if not mask.any():
        return None
    px = rgb[mask] / 255
    hsv = np.array([colorsys.rgb_to_hsv(*p) for p in px])
    h, s, v = hsv[:, 0] * 360, hsv[:, 1], hsv[:, 2]
    sel = s > 0.2
    if not sel.any():
        return h.mean(), s.mean(), v.mean()
    bins = (h[sel] // 18).astype(int) % 20
    weight = s[sel]
    tot = np.bincount(bins, weights=weight, minlength=20)
    top = tot.argmax()
    in_bin = sel.copy()
    in_bin[sel] = bins == top
    return h[in_bin].mean(), s[sel].mean(), v[sel].mean()

items = []
for path in sorted(glob.glob("out/tiles/composed/night_*.png")):
    name = os.path.basename(path)[len("night_"):-4]
    cls, level = name.rsplit("_", 1)
    hsv = avg_hsv(path)
    if hsv:
        items.append((cls, level, path, hsv))

print(f"{'class_level':<14} hue   sat   val")
for cls, level, path, (h, s, v) in items:
    print(f"{cls+'_'+level:<14} {h:5.0f} {s:4.2f} {v:4.2f}")

print("\nВозможные совпадения между разными классами (hue-расстояние < %.0f°, сравнение только цветных, sat>0.15):" % HUE_THRESH)
found = False
for (c1, l1, p1, (h1, s1, v1)), (c2, l2, p2, (h2, s2, v2)) in itertools.combinations(items, 2):
    if c1 == c2:
        continue
    if s1 < 0.15 or s2 < 0.15:
        continue
    dh = min(abs(h1 - h2), 360 - abs(h1 - h2))
    if dh < HUE_THRESH:
        found = True
        print(f"  {c1}_{l1} (h={h1:.0f}) ~ {c2}_{l2} (h={h2:.0f})  Δhue={dh:.0f}°")
if not found:
    print("  нет.")

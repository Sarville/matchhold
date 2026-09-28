"""Экспорт собранных листов монстров (out/anim/monsters/<имя>/<имя>_sheet.png) -> www/img/v2/monsters/<имя>.webp.
Запуск из rebranding/: python3 tools/export_monsters.py"""
import os
from PIL import Image

NAMES = ["zombie", "skeleton", "hauntedArmour", "demon", "rat", "spider", "waterElemental",
         "imp", "lizardman", "fireElemental", "warlock", "earthElemental", "lich"]
OUT = "../www/img/v2/monsters/"
os.makedirs(OUT, exist_ok=True)
for n in NAMES:
    src = f"out/anim/monsters/{n}/{n}_sheet.png"
    if not os.path.exists(src):
        print("нет", src); continue
    im = Image.open(src)
    dst = OUT + n + ".webp"
    im.save(dst, "WEBP", lossless=False, quality=90, alpha_quality=95, method=6)
    print(n, im.size, os.path.getsize(dst) // 1024, "KB")

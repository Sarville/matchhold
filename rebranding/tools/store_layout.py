"""Раскладка ячеек запаса по стадиям жилой линии (павильон-хранилище, 2.5D): ячейки стоят на полу в проёмах между стойками
(не поверх колонн). Пишет rebranding/store-layout.json и out/env/buildings/mock_store_layout.png. Запуск: cd out && python3 ../tools/store_layout.py
Координаты в логических px кадра спрайта жилой линии 100 x 106,7 (начало у левого верхнего угла). Замер по composed/*.png (960x1024, x9,6)."""
import json, random
from PIL import Image, ImageDraw

K = 9.6; PITCH = 8.5; CELL = 7.5          # шаг и размер ячейки (рамка в размер)
# стадия: (столбцов, рядов, [проёмы: (центр x px, ширина проёма px, число столбцов)], пол y px, низ балки y px)
STAGES = {"shack_1": (3, 3, [(427, 285, 3)], 968, 715), "house_2": (3, 4, [(432, 325, 3)], 925, 578),
          "fort_3": (4, 4, [(425, 340, 4)], 895, 570), "castle_4": (5, 4, [(427, 325, 4), (171, 67, 1)], 895, 570)}

if __name__ == "__main__":
    out = {"pitch": PITCH, "cell": CELL, "note": "ячейки 7,5 + зазор 1; порядок заполнения: индекс в списке cells (основной проём снизу вверх, затем левый проём)", "stages": {}}
    col = {"g": (242, 193, 78), "w": (176, 122, 78), "s": (154, 160, 166), "c": (198, 86, 69), "l": (126, 87, 194)}
    random.seed(3); tiles = []
    for n, (cols, rows, bays, floor, beam) in STAGES.items():
        cells = []
        for bi, (cx, w, nc) in enumerate(bays):
            bw = nc * PITCH; left = cx / K - bw / 2
            for c in range(nc):
                for r in range(rows):                # r = 0 нижний ряд
                    cells.append([round(left + c * PITCH, 2), round(floor / K - (r + 1) * PITCH + (PITCH - CELL), 2)])
        assert len(cells) == cols * rows, (n, len(cells))
        out["stages"][n] = {"capacity": len(cells), "cells": cells}
        im = Image.open(f"env/buildings/composed/{n}.png").convert("RGBA"); bg = Image.new("RGBA", im.size, (150, 190, 230, 255)); bg.alpha_composite(im)
        d = ImageDraw.Draw(bg)
        for i, (x, y) in enumerate(cells):
            k = random.choice("gwscl"); f = random.choice((0.2, 0.55, 1.0))
            d.rectangle([x * K, y * K, (x + CELL) * K, (y + CELL) * K], fill=(40, 26, 18, 255), outline=(20, 12, 8, 255), width=3)
            d.rectangle([x * K + 3, y * K + 3, x * K + 3 + (CELL * K - 6) * f, (y + CELL) * K - 3], fill=col[k] + (255,))
        tiles.append(bg.crop((0, 200, 960, 1024)).resize((480, 412)))
    json.dump(out, open("../store-layout.json", "w"), indent=1)
    sheet = Image.new("RGB", (960, 824)); [sheet.paste(t.convert("RGB"), ((i % 2) * 480, (i // 2) * 412)) for i, t in enumerate(tiles)]
    sheet.save("env/buildings/mock_store_layout.png"); print({n: s["capacity"] for n, s in out["stages"].items()})

"""T5: собирает 65 граней (плашка + иконка + ночью glow), tiles-manifest.json и листы tiles@1x/2x/3x.png.
Запуск из rebranding/: python3 tools/build_tiles.py. Выходы: out/tiles/composed/, out/tiles/sheets/, tiles-manifest.json.
Лист: 6 колонок × 19 рядов по 52 px (логических), как в игре (см. 02-tiles.md п. 2)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from compose_tiles import compose
from PIL import Image

K, KD, KN = "out/tiles/keyed/", "out/tiles/keyed-day/", "out/tiles/keyed-night/"
COL = dict(grain=0, stone=1, wood=2, clay=3, cloth=4, mana=5)
LEVELS = dict(grain=4, stone=9, wood=9, clay=4, cloth=4, mana=1)
DAY1 = dict(grain="grain_1_v2", wood="wood_1_v2", stone="stone_1_v2", clay="clay_1_v2", cloth="cloth_1_v8", mana="mana_1_v2")
DAYV = {"cloth_3": 2, "cloth_4": 2, "wood_2": 2, "wood_4": 2, "wood_8": 2, "wood_9": 3}  # остальные v1
NIGHT1 = dict(grain="grain_1_v1", stone="stone_1_v2", wood="wood_1_v1", clay="clay_1_v3", cloth="cloth_1_v1", mana="mana_1_v1")
NIGHTV = {"clay_3": 2, "stone_2": 5, "stone_3": 3, "wood_2": 2, "wood_3": 2,
          "cloth_2": 2, "clay_2": 2, "grain_4": 2, "clay_4": 2}  # сессия 7: ящер зелёный -> песочный (путался с grain),
          # паутина оранжевая -> красная, демон красно-оранжевый -> зелёный огонь (путался с огненными мечами stone),
          # зелье импа зелёное -> синее + другая форма (путалось с grain)
# glow ночью: цвет класса, у отдельных иконок свой (по сюжету)
G = dict(grain=(90, 220, 120), stone=(110, 170, 235), wood=(235, 165, 75), clay=(255, 125, 70), cloth=(165, 115, 255), mana=(225, 85, 205))
GO = {"clay_2": (255, 70, 55), "clay_3": (90, 165, 255), "clay_4": (70, 130, 235), "cloth_3": (255, 150, 50),
      **{f"stone_{i}": (255, 120, 60) for i in (4, 5, 6)}, **{f"stone_{i}": (140, 200, 255) for i in (7, 8, 9)},
      **{f"wood_{i}": (255, 205, 90) for i in (7, 8, 9)}}
DRAGON = dict(grain=((90, 230, 130), 0), clay=((120, 190, 255), 3), cloth=((255, 170, 50), 4))  # цвет, колонка

# порядок дерева по решению пользователя: бревно, 2 бревна, 3 бревна, доска, связка 2 досок, связка 4 досок; 7-9 без изменений
WOOD = {1: KD + "wood_4_v2.png", 2: K + "wood_1_v2.png", 3: KD + "wood_3_v1.png", 4: KD + "wood_2_v2.png", 5: KD + "wood_b2_v1.png", 6: KD + "wood_5_v1.png"}
def icon_day(c, l):
    if c == "wood" and l in WOOD: return WOOD[l]
    return K + DAY1[c] + ".png" if l == 1 else KD + f"{c}_{l}_v{DAYV.get(f'{c}_{l}', 1)}.png"
def icon_night(c, l): return KN + NIGHT1[c] + ".png" if l == 1 else KN + f"{c}_{l}_v{NIGHTV.get(f'{c}_{l}', 1)}.png"

def face(plate, icon, glow=None):
    """Кроп по bbox самой плашки (не по glow/тени), чтобы все грани были одного размера; glow за плашкой срезается."""
    box = Image.open(plate).convert("RGBA").getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    return compose(plate, icon, glow=glow).crop(box)

os.makedirs("out/tiles/composed", exist_ok=True); os.makedirs("out/tiles/sheets", exist_ok=True)
items = []  # (block, class, level, col, row, master)
for c in COL:
    for l in range(1, LEVELS[c] + 1):
        items.append(("day", c, l, COL[c], l - 1, face(K + "plate_day_v1.png", icon_day(c, l))))
        gl = (GO.get(f"{c}_{l}", G[c]), 0.85)
        items.append(("night", c, l, COL[c], 9 + l - 1, face(K + "plate_night_v2.png", icon_night(c, l), gl)))
for c, (col_, colidx) in DRAGON.items():
    items.append(("dragon", c, 1, COL[c], 18, face(K + "plate_night_v2.png", KN + f"dragon_{c}_v1.png", (col_, 1.0))))
# грани квадратные: приводим к одному размеру мастера
M = 384
man = []
for b, c, l, col, row, im in items:
    name = f"{b}_{c}_{l}.png"
    im.resize((M, M), Image.LANCZOS).save("out/tiles/composed/" + name)
    man.append(dict(file=name, block=b, cls=c, level=l, col=col, row=row))
json.dump(dict(cell=52, cols=6, rows=19, tiles=man), open("tiles-manifest.json", "w"), ensure_ascii=False, indent=1)
for s in (1, 2, 3):
    cell = 52 * s
    sheet = Image.new("RGBA", (6 * cell, 19 * cell), (0, 0, 0, 0))
    for (b, c, l, col, row, im) in items:
        sheet.alpha_composite(im.resize((cell, cell), Image.LANCZOS), (col * cell, row * cell))
    sheet.save(f"out/tiles/sheets/tiles{'' if s == 1 else f'@{s}x'}.png")
print(len(items), "граней; листы:", sheet.size)

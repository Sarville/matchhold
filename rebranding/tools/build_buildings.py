"""Здания: ключ фона -> альфа (key_layer.py), кроп по bbox, ОДИН масштаб на линию (min по стадиям: коробка 92% x 96% холста 768x1024,
самая большая стадия упирается в коробку, ранние остаются меньше), низ bbox = низ холста. Затем лист buildings{,@2x,@3x}.png и манифест.
Холст 768x1024 = 80x106,7 логических px (слот 80). Запуск из rebranding/: python3 tools/build_buildings.py
Выбор вариантов: SEL (стадия 1 и правки пользователя), остальные берутся из out/env/buildings/chain_<линия>.json (последняя попытка)."""
import json, os, subprocess
from PIL import Image

B = "out/env/buildings/"
W, H = 768, 1024
FIT_W, FIT_H = 0.92, 0.96
LOGICAL = (80, 106.7)
ROW = 107
HOME_W, HOME_XS = 100, 1.25                  # жилая линия (павильон-хранилище): слот и холст 100 логических px, горизонтальная растяжка спрайта x1,25 (по высоте без изменений)
HOME_YS = {"fort_3": 1.23, "castle_4": 1.23}   # вертикальная растяжка стадий жилой линии: проём под балкой не ниже, чем у house_2 (36 логических)
SLOT_W = 76                                  # остальные пять слотов: шаг 76, холст спрайта 80 (здание внутри ≤ 92%, зазор между зданиями ≥ 2)                                     # высота строки листа на 1x (80 x 107)
# линия: (ключ, первая стадия, [id стадий по порядку])
LINES = {
    "home": ("FF00FF", None, ["shack_1", "house_2", "fort_3", "castle_4"]),   # павильон-хранилище: chain_hall.json
    "bricklayer": ("FF00FF", "bricklayer_1_v3", [f"bricklayer_{i}" for i in range(1, 5)]),
    "weaver": ("00FF00", "weaver_1_v1", [f"weaver_{i}" for i in range(1, 5)]),
    "blacksmith": ("FF00FF", "blacksmith_1_v3", [f"blacksmith_{i}" for i in range(1, 9)]),
    "sawmill": ("FF00FF", "sawmill_1_v3", [f"sawmill_{i}" for i in range(1, 9)]),
    "gem": ("00FF00", None, [f"gem_{i}" for i in range(1, 5)]),
    "tower": ("FF00FF", "tower_2_v2", ["tower_1"]),
}
OVERRIDE = {}                                 # id -> файл-вариант (правки пользователя после ревью)
# порядок строк листа (как в старом buildings.png и sprites.js): blacksmith 0-7, bricklayer 8-11, sawmill 12-19, shack 20-23, tower 24-28 (gem_1..4 + tower_1), weaver 29-32
ORDER = ([f"blacksmith_{i}" for i in range(1, 9)] + [f"bricklayer_{i}" for i in range(1, 5)] + [f"sawmill_{i}" for i in range(1, 9)]
         + ["shack_1", "house_2", "fort_3", "castle_4"] + [f"gem_{i}" for i in range(1, 5)] + ["tower_1"] + [f"weaver_{i}" for i in range(1, 5)])

def variant(line, sid, first):
    if sid in OVERRIDE: return OVERRIDE[sid]
    if first and sid == LINES[line][2][0] and first: return first
    j = f"{B}chain_{ {'home': 'hall'}.get(line, line) }.json"
    return json.load(open(j))[sid]["file"] if os.path.exists(j) and sid in json.load(open(j)) else None

def keyed(name, key):
    os.makedirs(B + "keyed", exist_ok=True); k = f"{B}keyed/{name}.png"
    if not os.path.exists(k): subprocess.run(["python3", "tools/key_layer.py", f"{B}{name}.png", k, key], check=True)
    im = Image.open(k).convert("RGBA"); return im.crop(im.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox())

def bottom_width(im):
    """Ширина нижних 20% высоты (подставка кристалла)."""
    a = im.getchannel("A").point(lambda v: 255 if v > 10 else 0).crop((0, int(im.height * 0.8), im.width, im.height)); bb = a.getbbox(); return bb[2] - bb[0]

def canvas_w(line): return round(HOME_W * W / 80) if line == "home" else W

def build():
    os.makedirs(B + "composed", exist_ok=True); done = {}
    for line, (key, first, ids) in LINES.items():
        files = {sid: variant(line, sid, first) for sid in ids}
        ims = {sid: keyed(f, key) for sid, f in files.items() if f}
        if not ims: continue
        if line == "gem":     # подставка одной ширины у всех четырёх состояний, подставка не шире 50% холста
            ref = max(bottom_width(im) for im in ims.values()); f = {sid: ref / bottom_width(im) for sid, im in ims.items()}; cap = 0.5 * W / ref
        else:                 # размер стадии не меньше предыдущей (ИИ рисует масштаб как хочет): метрика sqrt(w*h), бегущий максимум
            f = {}; t = 0
            for sid in ids:
                if sid in ims: m = (ims[sid].width * ims[sid].height) ** .5; t = max(t, m); f[sid] = t / m
            cap = 1e9
        cw = canvas_w(line); xs = HOME_XS if line == "home" else 1
        ys = {sid: (HOME_YS.get(sid, 1) if line == "home" else 1) for sid in ims}
        r = min(cap, min(min(FIT_W * cw / (im.width * f[sid] * xs), FIT_H * H / (im.height * f[sid] * ys[sid])) for sid, im in ims.items()))   # общий масштаб линии
        for sid, im in ims.items():
            k = r * f[sid]; s = im.resize((round(im.width * k * xs), round(im.height * k * ys[sid])), Image.LANCZOS)
            c = Image.new("RGBA", (cw, H), (0, 0, 0, 0)); c.alpha_composite(s, ((cw - s.width) // 2, H - s.height)); c.save(f"{B}composed/{sid}.png"); done[sid] = files[sid]
    return done

def sheet(done):
    """Лист: ячейка 100 x 107, строки жилой линии на всю ширину (100), остальные 80 x 107 у левого края (CSS width: 80, background-position 0)."""
    home = {"shack_1", "house_2", "fort_3", "castle_4"}; widths = {i: (HOME_W if i in home else 80) for i in ORDER}
    # позиции слотов (центры, `position` в gamecontent.js): слот жилой линии 0..100, остальные пять с шагом 76 до 480
    centres = {"home": HOME_W // 2, **{n: HOME_W + SLOT_W * i + SLOT_W // 2 for i, n in enumerate(["bricklayer", "weaver", "blacksmith", "sawmill", "tower"])}}
    man = {"cell": [HOME_W, ROW], "widths": widths, "rows": {i: n for n, i in enumerate(ORDER)}, "slot_centres": centres, "dude_spot_note": "dudeSpot = position + width/2 (правый край здания), как в building.js",
           "built": [i for i in ORDER if i in done], "sources": done}
    os.makedirs(B + "sheets", exist_ok=True)
    for sc, sfx in ((1, ""), (2, "@2x"), (3, "@3x")):
        sh = Image.new("RGBA", (HOME_W * sc, ROW * sc * len(ORDER)), (0, 0, 0, 0))
        for n, i in enumerate(ORDER):
            if i in done: sh.alpha_composite(Image.open(f"{B}composed/{i}.png").resize((widths[i] * sc, ROW * sc), Image.LANCZOS), (0, n * ROW * sc))
        sh.save(f"{B}sheets/buildings{sfx}.png")
    json.dump(man, open("buildings-manifest.json", "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    d = build(); sheet(d); print(len(d), "спрайтов:", sorted(d))

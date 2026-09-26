"""Капсулы стройки на 1/2/3 ресурса из ОДНОЙ трёхсегментной каменной объёмной плиты (capsule_block3_v2, верхняя плоскость нарисована в арте): геометрию (лунки, жёлобы, оси, швы)
замеряем по тёмным вырезам, режем по швам/осям сегментов, из жёлоба вырезаем середину (он однородный, шва не видно), чтобы
ширина = LOGICAL_W, шаг сегмента = TARGET_PITCH логических px, круги не искажены.
Запуск из rebranding/: python3 tools/build_capsules.py
Пишет out/env/capsules/composed/capsule_{1,2,3}.png и capsules.json (лунки и жёлобы в px холста и в логических px)."""
import json, os
import numpy as np
from PIL import Image, ImageChops, ImageDraw
from scipy import ndimage as ndi

C = "out/env/capsules/"
SRC = C + "keyed/capsule_block3_v2.png"
LOGICAL_W = 76          # слот 80 минус по 2 px
TARGET_PITCH = 10       # логических px на сегмент (лунка ~7)
INSET, RADIUS = 8, 14   # срез бахромы по краю и скругление углов (px исходника)
TOP_PX = 52           # высота верхней плоскости в исходнике (от верха до передней грани, замер по capsule_block3_v2)
STAND = 0.8            # низ поставленного здания: доля глубины верхней плоскости от её заднего края
GROUND_SRC = {"": "out/env/ground/keyed/ground_strip_v2.png", "_night": "out/env/ground/keyed/ground_strip_night_v1.png"}; GROUND_D = 14; CAP_W = 22; GROUND_STAND = 0.4   # мини-фон на рельсе: глубина (логических px), ступни на 40% от переднего края

def measure(im):
    a = np.array(im).astype(int); lum = a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
    m = ndi.binary_opening((lum < 65) & (a[..., 3] > 200), iterations=2); l, n = ndi.label(m); sl = ndi.find_objects(l)
    bl = sorted([(sl[i][0].start, sl[i][0].stop, sl[i][1].start, sl[i][1].stop) for i in range(n) if ndi.sum(m, l, i + 1) > 3000])
    bl = bl[:6]   # седьмой тёмный объект (тёмный цоколь снизу) не жёлоб
    assert len(bl) == 6, bl
    rows = [sorted(bl[i:i + 1] + bl[i + 1:i + 2], key=lambda b: b[2]) for i in (0, 2, 4)]   # (лунка, жёлоб) по рядам
    cy = [(r[0][0] + r[0][1]) / 2 for r in rows]
    return {"box": Image.fromarray(a[..., 3].astype(np.uint8)).point(lambda v: 255 if v > 10 else 0).getbbox(), "cy": cy,
            "sock": (min(r[0][2] for r in rows), max(r[0][3] for r in rows)), "trough": (min(r[1][2] for r in rows), max(r[1][3] for r in rows)),
            "sock_d": np.mean([r[0][1] - r[0][0] for r in rows]), "trough_h": np.mean([r[1][1] - r[1][0] for r in rows])}

def build(n, g, src):
    box, cy = g["box"], g["cy"]; pitch = (cy[2] - cy[0]) / 2
    seam = ((cy[0] + cy[1]) / 2, (cy[1] + cy[2]) / 2)
    strips, axes = {3: ([(box[1], box[3])], (0, 1, 2)), 2: ([(box[1], seam[0]), (seam[1], box[3])], (0, 2)),
                    1: ([(box[1], cy[0]), (cy[2], box[3])], (0,))}[n]
    W = box[2] - box[0]; wf = round(LOGICAL_W * pitch / TARGET_PITCH); cut = W - wf
    assert cut > 0, "капсула уже целевой ширины"
    tm = (g["trough"][0] + g["trough"][1]) / 2; c0 = round(tm - cut / 2); c1 = c0 + cut     # вырезаемая середина жёлоба
    out = Image.new("RGBA", (wf, round(sum(b - a for a, b in strips)))); y = 0; pos = {}
    for y0, y1 in strips:
        s = src.crop((box[0], round(y0), box[2], round(y1))); a_, b_ = c0 - box[0], c1 - box[0]
        r = Image.new("RGBA", (wf, s.height)); r.paste(s.crop((0, 0, a_, s.height)), (0, 0)); r.paste(s.crop((b_, 0, s.width, s.height)), (a_, 0))
        out.paste(r, (0, y))
        for i in axes:
            if i not in pos and y0 <= cy[i] <= y1: pos[i] = y + cy[i] - y0
        y += s.height
    m = Image.new("L", out.size, 0); ImageDraw.Draw(m).rounded_rectangle([INSET, INSET, out.width - 1 - INSET, out.height - 1 - INSET], RADIUS, fill=255)
    out.putalpha(ImageChops.multiply(out.getchannel("A"), m)); out = out.crop((INSET, INSET, out.width - INSET, out.height - INSET))
    k = LOGICAL_W / out.width; dx = box[0] + INSET
    sc = lambda r: [round(v * k, 2) for v in r]; segs = []
    for i in axes:
        c = pos[i] - INSET
        segs.append({"socket": sc([g["sock"][0] - dx, c - g["sock_d"] / 2, g["sock"][1] - g["sock"][0], g["sock_d"]]),
                     "trough": sc([g["trough"][0] - dx, c - g["trough_h"] / 2, g["trough"][1] - g["trough"][0] - cut, g["trough_h"]])})
    return out, {"px": out.size, "logical": [LOGICAL_W, round(out.height * k, 1)], "top_depth": round(TOP_PX * k, 2), "stand": round(STAND * TOP_PX * k, 2), "segments": segs}

if __name__ == "__main__":
    os.makedirs(C + "composed", exist_ok=True); src = Image.open(SRC).convert("RGBA"); g = measure(src); meta = {}
    for n in (1, 2, 3):
        im, meta[n] = build(n, g, src); im.save(f"{C}composed/capsule_{n}.png")
    k = LOGICAL_W / meta[3]["px"][0]
    for sfx, gsrc in GROUND_SRC.items():   # мини-фон день и ночь: одинаковая геометрия
        g = Image.open(gsrc).convert("RGBA"); g = g.crop(g.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox())
        g = g.crop((0, 0, g.width, g.height - 4))                                   # срезаем размазанную кромку ключа снизу
        gh = round(GROUND_D / k); g = g.resize((round(g.width * gh / g.height), gh), Image.LANCZOS)
        t = Image.new("RGBA", (g.width * 2, gh)); t.paste(g, (0, 0)); t.paste(g.transpose(Image.FLIP_LEFT_RIGHT), (g.width, 0)); t.save(f"{C}composed/ground_tile{sfx}.png")
        cw = round(CAP_W / k); yy, xx = np.mgrid[0:gh, 0:cw]   # торец: четверть эллипса от нижнего внешнего угла к основанию столбика (центр столбика на CAP_W от края)
        m = (((xx - cw) / cw) ** 2 + ((yy - gh) / gh) ** 2 <= 1).astype(np.uint8) * 255
        cap = t.crop((0, 0, cw, gh)); cap.putalpha(ImageChops.multiply(cap.getchannel("A"), Image.fromarray(m)))
        cap.save(f"{C}composed/ground_cap_l{sfx}.png"); cap.transpose(Image.FLIP_LEFT_RIGHT).save(f"{C}composed/ground_cap_r{sfx}.png")
        meta["ground" + sfx] = {"cap_px": cap.size, "cap_logical": [CAP_W, GROUND_D], "px": t.size, "logical": [round(t.width * k, 1), GROUND_D], "stand": round(GROUND_STAND * GROUND_D, 2)}   # повтор по x
    json.dump(meta, open(C + "capsules.json", "w"), indent=1)
    print(json.dumps({n: (m["px"], m["logical"]) for n, m in meta.items()}), g)

#!/usr/bin/env python3
"""Векторная анимированная эмблема Matchhold (Lottie, 96x96, петля 2.4 с).
Используется как иконка экрана запуска VK (<=24 КБ) и сплэш Android (lottie-android).
Запуск: python3 tools/gen_lottie.py  -> publish/vk/launch/matchhold_lottie_96.json
       и android/app/src/main/res/raw/splash_lottie.json"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTS = [os.path.join(ROOT, "publish/vk/launch/matchhold_lottie_96.json"),
        os.path.join(ROOT, "android/app/src/main/res/raw/splash_lottie.json")]
FR, OP = 30, 72
EASE = ({"x": 0.42, "y": 0}, {"x": 0.58, "y": 1})

GOLD, GOLD_D = "#E8B33A", "#B5791E"
BLUE, BLUE_D = "#2F58A8", "#1F3E82"
STONE, STONE_D = "#DDD0B2", "#B7A987"
WOOD, WOOD_D = "#8F5B2E", "#5E3A1C"
STEEL, STEEL_D = "#C9CCD4", "#8E929C"
LEAF, LEAF_D = "#67A744", "#437A2C"
AMBER = "#FFC65A"


def col(h):
    return [round(int(h[i:i + 2], 16) / 255, 2) for i in (1, 3, 5)] + [1]


def r1(v):
    return round(v, 1)


def prop(v):
    return {"a": 0, "k": v}


def anim(keys):
    """keys: [(frame, value_list)] -> animated property, one shared ease; последний ключ без ease."""
    out = []
    for n, (t, v) in enumerate(keys):
        k = {"t": t, "s": [r1(x) for x in v]}
        if n < len(keys) - 1:
            d = len(v)
            k["i"] = {"x": [EASE[1]["x"]] * d, "y": [EASE[1]["y"]] * d}
            k["o"] = {"x": [EASE[0]["x"]] * d, "y": [EASE[0]["y"]] * d}
        out.append(k)
    return {"a": 1, "k": out}


def poly(pts, closed=True):
    return {"ty": "sh", "ks": prop({"i": [[0, 0]] * len(pts), "o": [[0, 0]] * len(pts),
                                     "v": [[r1(x), r1(y)] for x, y in pts], "c": closed})}


def bez(pts):
    """pts: (x, y, inx, iny, outx, outy) — касательные относительно вершины."""
    return {"ty": "sh", "ks": prop({"i": [[p[2], p[3]] for p in pts], "o": [[p[4], p[5]] for p in pts],
                                     "v": [[p[0], p[1]] for p in pts], "c": True})}


def rect(cx, cy, w, h, r=0):
    return {"ty": "rc", "p": prop([cx, cy]), "s": prop([w, h]), "r": prop(r)}


def ell(cx, cy, w, h):
    return {"ty": "el", "p": prop([cx, cy]), "s": prop([w, h])}


def fill(h, o=100):
    return {"ty": "fl", "c": prop(col(h)), "o": prop(o), "r": 1}


def stroke(h, w):
    return {"ty": "st", "c": prop(col(h)), "o": prop(100), "w": prop(w), "lc": 2, "lj": 2, "ml": 4}


TR = lambda: {"ty": "tr", "o": prop(100)}


def g(*items, tr=None):
    return {"ty": "gr", "it": list(items) + [tr or TR()]}


def solid(geom, color, edge=None, ew=1):
    items = [geom, fill(color)]
    if edge:
        items.insert(1, stroke(edge, ew))
    return g(*items)


def layer(ind, name, shapes=(), ks=None, parent=None, ty=4):
    L = {"ind": ind, "ty": ty, "nm": name, "ks": ks or {"o": prop(100)}, "ip": 0, "op": OP, "st": 0}
    if parent:
        L["parent"] = parent
    if ty == 4:
        L["shapes"] = list(shapes)
    return L


def pivot(cx, cy, **kw):
    d = {"a": prop([cx, cy]), "p": prop([cx, cy])}
    d.update(kw)
    return d


def star(r):
    k = r * 0.24
    return poly([(0, -r), (k, -k), (r, 0), (k, k), (0, r), (-k, k), (-r, 0), (-k, -k)])


def flag_pts(phase):
    base = [(48, 9), (55, 7), (62, 9), (68, 8), (64, 12.5), (68, 17), (62, 17.5), (55, 15.5), (48, 14)]
    return [(x, y + 1.7 * math.sin(0.34 * (x - 48) - phase) * min(1, (x - 48) / 6)) for x, y in base]


# ---- слои (сверху вниз: первый рисуется поверх) ----
layers = []
ROOT_ID = 1


BODY_ID = 2


def add(*a, parent=BODY_ID, **k):
    layers.append(layer(len(layers) + 3, *a, parent=parent, **k))


def sparkle(name, cx, cy, t0, size):
    s = anim([(t0, [0, 0]), (t0 + 12, [100, 100]), (t0 + 24, [0, 0]), (OP, [0, 0])])
    r = anim([(t0, [0]), (t0 + 24, [90]), (OP, [90])])
    add(name, [g(star(size), fill("#FFFDF2"))], ks={"p": prop([cx, cy]), "s": s, "r": r})


sparkle("spark1", 31, 30, 10, 5.5)
sparkle("spark2", 78, 17, 40, 4.5)

# флаг: путь с 4 фазами волны
fk = [{"t": t, "s": [{"i": [[0, 0]] * 9, "o": [[0, 0]] * 9,
                       "v": [[r1(x), r1(y)] for x, y in flag_pts(2 * math.pi * n / 4)], "c": True}]}
      for n, t in enumerate((0, 18, 36, 54, 72))]
for k in fk[:-1]:
    k["i"] = {"x": [0.5], "y": [1]}
    k["o"] = {"x": [0.5], "y": [0]}
flag_path = {"ty": "sh", "ks": {"a": 1, "k": fk}}
add("flag", [g(flag_path, fill(BLUE), stroke(GOLD, 1.2))])
add("flagdot", [g(ell(0, 0, 3.6, 3.6), fill(GOLD))],
    ks={"p": anim([(t, [57, 12 + 1.7 * math.sin(0.34 * 9 - 2 * math.pi * n / 4) * 1.0])
                   for n, t in enumerate((0, 18, 36, 54, 72))])})
add("pole", [solid(rect(48, 12, 1.8, 18), GOLD, None), solid(ell(48, 3.5, 4, 4), GOLD)])

# окна башни (мерцание)
add("win_r", [solid(rect(52.5, 41, 3, 6.5, 1.4), AMBER)],
    ks={"o": anim([(0, [60]), (36, [100]), (72, [60])])})
add("win_l", [solid(rect(43.5, 41, 3, 6.5, 1.4), AMBER)],
    ks={"o": anim([(0, [100]), (36, [60]), (72, [100])])})

# башня
door = bez([(43.5, 66, 0, 0, 0, 0), (43.5, 58, 0, 0, 0, -3.5), (48, 53, -3.5, 0, 3.5, 0),
            (52.5, 58, 0, -3.5, 0, 0), (52.5, 66, 0, 0, 0, 0)])
add("door", [solid(door, WOOD, WOOD_D, 0.8), solid(rect(48, 60, 0.9, 12), WOOD_D)])
add("banners", [solid(rect(30.5, 52, 4.4, 8, 0.8), BLUE_D, GOLD, 0.7), solid(rect(65.5, 52, 4.4, 8, 0.8), BLUE_D, GOLD, 0.7)])
merl = lambda x0, x1, y, n: [solid(rect(x0 + (x1 - x0) * (i + .5) / n, y, (x1 - x0) / n * 0.55, 3.4, 0.4), STONE, STONE_D, 0.6) for i in range(n)]
add("towers", [
    g(poly([(41, 30), (48, 17), (55, 30)]), fill(BLUE), stroke(BLUE_D, 0.8)),
    *merl(37.5, 58.5, 33.5, 5),
    solid(rect(48, 50, 21, 32, 1), STONE, STONE_D, 1),
    *merl(26.5, 37, 45, 3), solid(rect(31.75, 56, 10, 20, 0.8), STONE, STONE_D, 1),
    *merl(59, 69.5, 45, 3), solid(rect(64.25, 56, 10, 20, 0.8), STONE, STONE_D, 1),
])

# медальон и щит
add("medal", [solid(ell(48, 77, 8.5, 8.5), GOLD, GOLD_D, 0.8), solid(ell(48, 77, 3.6, 3.6), GOLD_D)])
shield = bez([(21, 32, 0, 0, 0, 0), (48, 21, -12, 3, 12, -3), (75, 32, 0, 0, 0, 0),
              (75, 55, 0, -7, 0, 9), (48, 79, 13, -6, -13, -6), (21, 55, 0, 9, 0, -7)])
add("shield", [g(shield, fill(BLUE), stroke(GOLD, 3.2)),
               g(ell(23, 33, 5, 5), fill(GOLD_D)), g(ell(73, 33, 5, 5), fill(GOLD_D)),
               g(ell(23, 33, 3.4, 3.4), fill(GOLD)), g(ell(73, 33, 3.4, 3.4), fill(GOLD))])

# лента и медальон
add("ribbon_l", [solid(poly([(45, 79), (39, 79), (34, 93), (40, 89.5), (43, 94)]), BLUE, GOLD, 1)])
add("ribbon_r", [solid(poly([(51, 79), (57, 79), (62, 93), (56, 89.5), (53, 94)]), BLUE, GOLD, 1)])

# лавр (лёгкое качание)
leaf = lambda x, y, rot, c: g(ell(0, 0, 9, 4.6), fill(c),
                             tr={"ty": "tr", "p": prop([x, y]), "a": prop([0, 0]), "s": prop([100, 100]),
                                 "r": prop(rot), "o": prop(100)})
lp = [(16, 68, -55), (14, 60, -75), (14, 52, -100), (17, 45, -120), (22, 74, -35)]
for side, sgn in (("l", 1), ("r", -1)):
    sh = []
    for i, (x, y, rot) in enumerate(lp):
        xx = x if sgn == 1 else 96 - x
        rr = rot if sgn == 1 else 180 - rot
        sh.append(leaf(xx, y, rr, LEAF if i % 2 == 0 else LEAF_D))
    add("laurel_" + side, sh,
        ks=pivot(20 if sgn == 1 else 76, 78, r=anim([(0, [0]), (36, [2.2 * sgn]), (72, [0])])))

# молот (голова слева сверху) и меч — за щитом; строятся вертикально вокруг (48,48), крутятся
hammer = [
    solid(rect(48, 10, 5, 19, 0.8), GOLD, GOLD_D, 0.7),
    solid(rect(48, 10, 25, 17, 3.2), STEEL, STEEL_D, 1),
    solid(rect(48, 89, 9, 6, 2), GOLD, GOLD_D, 0.8),
    solid(rect(48, 50, 4.8, 82, 1.2), WOOD, WOOD_D, 0.8),
]
sword = [
    solid(poly([(48, 2), (53.5, 9), (53.5, 44), (42.5, 44), (42.5, 9)]), STEEL, STEEL_D, 0.9),
    solid(rect(48, 26, 1.2, 34), "#F2F3F7"),
    solid(rect(48, 47, 20, 4.2, 1.6), GOLD, GOLD_D, 0.8),
    solid(rect(48, 63, 4.4, 26, 1.2), WOOD, WOOD_D, 0.8),
    solid(ell(48, 86, 6.4, 6.4), GOLD, GOLD_D, 0.8),
]
add("sword", sword, parent=ROOT_ID, ks=pivot(48, 48, r=anim([(0, [43]), (36, [39]), (72, [43])])))
add("hammer", hammer, parent=ROOT_ID, ks=pivot(48, 48, r=anim([(0, [-43]), (36, [-47]), (72, [-43])])))

# корневой null: дыхание эмблемы
layers.insert(0, layer(BODY_ID, "body", ty=3, parent=ROOT_ID, ks=pivot(48, 50, s=prop([80, 80]))))
layers.insert(0, layer(ROOT_ID, "root", ty=3, ks=pivot(
    48, 48,
    p=anim([(0, [48, 49]), (36, [48, 46.5]), (72, [48, 49])]),
    s=anim([(0, [97, 97]), (36, [100, 100]), (72, [97, 97])]))))

doc = {"v": "5.7.0", "fr": FR, "ip": 0, "op": OP, "w": 96, "h": 96, "nm": "matchhold", "assets": [], "layers": layers}

if __name__ == "__main__":
    txt = json.dumps(doc, separators=(",", ":"))
    for p in OUTS:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(txt)
    print(len(txt), "bytes", OUTS[0])

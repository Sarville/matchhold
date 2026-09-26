"""Мок полосы мира (гейт 2b): здания и капсулы в масштабе над полем, день. Запуск: cd out && python3 ../tools/mock_world.py
Геометрия по 01-environment.md «Геометрия полосы мира»: земля = верхний внешний край рамки, слоты 80i, здание 80x106,7, полоса 140."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import mock_all as M
from PIL import Image
M.S = os.environ.get("S", "/tmp/claude-1000/-home-user-projects-matchhold/8cf97f12-1c34-4a07-9e32-fb51c227da2b/scratchpad/")
BLD = "env/buildings/composed/"
BH = 320 / 3                      # высота спрайта (логических px)
CEN = [50, 138, 214, 290, 366, 442]   # центры слотов (`position`): жилой слот 0..100, остальные пять шагом 76 (см. buildings-manifest.json)
HOME = {"shack_1", "house_2", "fort_3", "castle_4"}
wid = lambda n: 100 if n in HOME else 80   # ширина спрайта
GROUND_D, GROUND_STAND = 14, 5.6   # мини-фон на рельсе (земля, дорожка, трава): глубина и высота ступней над передним краем, логических px
ORDER = ["shack_1", "bricklayer_1", "weaver_1", "blacksmith_1", "sawmill_1", "tower_1"]   # слоты 0..5

def ledge(v, x0, x1, ground, k, night=False):
    """Мини-фон на верху рельса от внешнего края до внешнего края: закруглённые торцы (спрайты ground_cap_l/r, поднимаются к основанию столбика) + повтор плитки по x между ними."""
    sfx = "_night" if night else ""; C = "env/capsules/composed/"
    def sc(im): return im.resize((max(1, round(im.width * GROUND_D * k / im.height)), round(GROUND_D * k)), Image.LANCZOS)
    t, cl, cr = sc(M.load(C + f"ground_tile{sfx}.png")), sc(M.load(C + f"ground_cap_l{sfx}.png")), sc(M.load(C + f"ground_cap_r{sfx}.png"))
    xa, xb = x0 + cl.width, x1 - cr.width; x = xa
    while x < xb: v.alpha_composite(t.crop((0, 0, min(t.width, xb - x), t.height)), (x, ground - t.height)); x += t.width
    v.alpha_composite(cl, (x0, ground - cl.height)); v.alpha_composite(cr, (x1 - cr.width, ground - cr.height))

def foot(ground, k):
    """Низ здания на земле: ступни стоят на дорожке, GROUND_STAND над передним краем."""
    return ground - round(GROUND_STAND * k)

def world(v, xo, ground, k, night=False):
    """Кладёт 6 зданий на уступ (ground = y переднего края уступа в px), xo = x левого края проёма, k = px на логический px."""
    for i, n in enumerate(ORDER):
        p = os.path.join(BLD, n + ".png")
        if os.path.exists(p):
            v.alpha_composite(M.sz(M.load(p), round(wid(n) * k), round(BH * k)), (round(xo + (CEN[i] - wid(n) / 2) * k), foot(ground, k) - round(BH * k)))

import json
from PIL import ImageDraw
CAPS = json.load(open("env/capsules/capsules.json"))
COL = {"stone": (154, 160, 166), "wood": (176, 122, 78), "clay": (198, 86, 69), "cloth": (126, 87, 194)}
ICON = {"stone": "stone_1_v2", "wood": "wood_1_v2", "clay": "clay_1_v3", "cloth": "cloth_1_v8"}

def capsule(fills, k):
    """Капсула по числу ресурсов: рама + заливка по жёлобу + иконка в лунке (это делает игра, здесь имитация для мока)."""
    n = len(fills); m = CAPS[str(n)]; W, H = round(m["logical"][0] * k), round(m["logical"][1] * k)
    im = M.sz(M.load(f"env/capsules/composed/capsule_{n}.png"), W, H); K = 4
    for f, seg in zip(fills, m["segments"]):
        cls, frac = f; x, y, w, h = [v * k for v in seg["trough"]]; inset = 0.12 * h
        ov = Image.new("RGBA", (round(w * K), round(h * K)), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        fw = (w - 2 * inset) * frac
        if fw > 0: d.rounded_rectangle([inset * K, inset * K, (inset + fw) * K, (h - inset) * K], (h - 2 * inset) * K / 2, fill=COL[cls] + (255,))
        im.alpha_composite(ov.resize((round(w), round(h)), Image.LANCZOS), (round(x), round(y)))
        sx, sy, sw, sh = [v * k for v in seg["socket"]]
        for p in ("keyed/" + ICON[cls] + ".png",):
            ic = M.trim(M.load("tiles/" + p)); s_ = round(sw * 0.86); ic = M.sz(ic, s_, s_ if ic.width == ic.height else None)
            im.alpha_composite(ic, (round(sx + (sw - ic.width) / 2), round(sy + (sh - ic.height) / 2)))
    return im

def building_site(v, xo, ground, k):
    """Стройка: слот 0 предшественник поднят и стоит на верхней грани 3-сегментной капсулы, слоты 1 и 2 пустые с капсулой 1 и 2, остальные стоят."""
    slot = lambda i: round(xo + (CEN[i] - 38) * k); big = lambda n: M.sz(M.load(BLD + n + ".png"), round(wid(n) * k), round(BH * k)); cx = 0   # slot(i) = левый край капсулы 76 шириной, по центру слота
    base = foot(ground, k)                                          # капсулы стоят на земле так же, как здания
    cap3 = capsule([("stone", .8), ("wood", .5), ("clay", .1)], k); st = round(CAPS["3"]["stand"] * k)
    v.alpha_composite(cap3, (slot(0) + cx, base - cap3.height))
    v.alpha_composite(big("shack_1"), (round(xo + (CEN[0] - 50) * k), base - cap3.height + st - round(BH * k)))                 # низ здания на верхней грани капсулы
    c1 = capsule([("wood", .6)], k); v.alpha_composite(c1, (slot(1) + cx, base - c1.height))
    c2 = capsule([("stone", .3), ("cloth", .9)], k); v.alpha_composite(c2, (slot(2) + cx, base - c2.height))
    for i, n in enumerate(ORDER[3:], 3): v.alpha_composite(big(n), (round(xo + (CEN[i] - wid(n) / 2) * k), base - round(BH * k)))

import json as _j
from PIL import ImageFont
SIGNS = _j.load(open("env/signs/signs.json"))

def signs(v, xL, xR, ground, k, night, day_n=12, level=7, port=False):
    """Столбики по краям: слева день + фаза (значок рисует игра), справа уровень. Стоят на углах рамки, ступни на линии мини-фона."""
    st = "night" if night else "day"; sg = M.sz(M.load(f"env/signs/composed/sign_{st}.png"), round(44 * k), round(84 * k)); sf = SIGNS["safe"]
    ttf = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; fnt = lambda pt: ImageFont.truetype(ttf, max(6, round(pt * k))) if os.path.exists(ttf) else ImageFont.load_default()
    for x, txt, icon in ((xL, str(day_n), True), (xR, str(level), False)):
        y = ground - sg.height; im = sg.copy(); d = ImageDraw.Draw(im); font = fnt(11 if icon and not port else 15)
        cx, cy = (sf[0] + sf[2] / 2) * k, (sf[1] + sf[3] / 2) * k
        if icon and not port:   # значок фазы над числом: солнце или луна (набросок для мока)
            r = 3.4 * k; iy = sf[1] * k + r + 0.6 * k; cy += 2.4 * k
            d.ellipse([cx - r, iy - r, cx + r, iy + r], fill=(150, 170, 230) if night else (255, 200, 60))
            if night: d.ellipse([cx - r + 2 * k, iy - r - 0.4 * k, cx + r + 2 * k, iy + r - 0.4 * k], fill=(46, 56, 83))
        d.text((cx, cy), txt, font=font, fill=(235, 200, 110) if night else (92, 58, 34), anchor="mm")
        v.alpha_composite(im, (x, y))

def scene(port, site=False, night=False):
    if not port:
        vw, vh = 1920, 1080; v, fg = M.layers(night, False, vw, vh)
        k = 1.32; B = int(480 * k); F = int(B * 2048 / 1684); b, o, ob = M.board(night, F)
        strip = int(150 * k); hud = 84; y0 = (vh - (strip + F + hud)) // 2; xF = (vw - F) // 2; yF = y0 + strip - 12
    else:
        vw, vh = 390, 844; v, fg = M.layers(night, True, vw, vh)
        F = vw - 8; B = int(F * 1684 / 2048); b, o, ob = M.board(night, F); k = B / 480   # мир 560 логических = 480 * 1,1667: слот 93, здания x1,17
        strip = int(150 * k); hud = 50; y0 = (vh - (strip + F + hud)) // 2; xF = (vw - F) // 2; yF = y0 + strip - 4
    v.alpha_composite(b, (xF, yF)); edge = int(32 / 2048 * F)
    ledge(v, xF + edge, xF + F - edge, yF + edge, k, night)   # от края до края, торцы закруглены к основаниям столбиков (центр столбика на 22)
    if not night: (building_site if site else world)(v, xF + o, yF + edge, k)
    signs(v, xF + edge, xF + F - edge - round(44 * k), yF + edge, k, night, port=port)
    v.alpha_composite(fg)
    return v.convert("RGB"), (xF, yF, F, k)

if __name__ == "__main__":
    d, (xF, yF, F, k) = scene(False); d.crop((xF - 30, max(0, yF - int(160 * k)), xF + F + 30, yF + int(F * 0.30))).save("env/mock_world_desktop_day.png")
    d, (xF, yF, F, k) = scene(False, True); d.crop((xF - 30, max(0, yF - int(160 * k)), xF + F + 30, yF + int(F * 0.30))).save("env/mock_world_site_desktop_day.png")
    for nt in (False, True):
        t = "night" if nt else "day"
        d, (xF, yF, F, k) = scene(False, False, nt); d.crop((xF - 30, max(0, yF - int(160 * k)), xF + F + 30, yF + int(F * 0.30))).save(f"env/mock_world_desktop_{t}.png")
        p, (xF, yF, F, k) = scene(True, False, nt); p = p.crop((0, max(0, yF - int(150 * k)), 390, yF + int(F * 0.35))); p.resize((780, p.height * 2)).save(f"env/mock_world_portrait_{t}.png")
    ORDER[:] = ["castle_4", "bricklayer_4", "weaver_4", "blacksmith_8", "sawmill_8", "tower_1"]   # максимальные стадии всех линий
    d, (xF, yF, F, k) = scene(False); d.crop((xF - 30, max(0, yF - int(160 * k)), xF + F + 30, yF + int(F * 0.30))).save("env/mock_world_max_desktop_day.png")
    p, (xF, yF, F, k) = scene(True); p = p.crop((0, max(0, yF - int(150 * k)), 390, yF + int(F * 0.35))); p = p.resize((780, p.height * 2)); p.save("env/mock_world_max_portrait_day.png")

"""Экспорт готового арта из rebranding/out в www/img/v2 (WebP, x2 от логических px). Запуск из rebranding/:
    python3 tools/export_www.py [группа ...]     группы: board tiles world hud bg (без аргументов: все)
Геометрия и константы: 01-environment.md («Геометрия полосы мира»), сессия 5 (встраивание).
Кэш keyed-слоёв фона: /tmp/mm_keyed (ключ #FF00FF у слоёв land mid)."""
import os, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from scipy import ndimage as ndi

OUT = "../www/img/v2/"
E = "out/env/"; I = "out/icons/keyed/"
CACHE = "/tmp/mm_keyed/"
os.makedirs(OUT, exist_ok=True); os.makedirs(OUT + "bg", exist_ok=True); os.makedirs(CACHE, exist_ok=True)


def load(p): return Image.open(p).convert("RGBA")
def trim(im, thr=10):
    bb = im.getchannel("A").point(lambda v: 255 if v > thr else 0).getbbox(); return im.crop(bb)
def sz(im, w=None, h=None):
    if w is None: w = round(im.width * h / im.height)
    if h is None: h = round(im.height * w / im.width)
    return im.resize((w, h), Image.LANCZOS)
def save(im, name, lossless=True, q=85):
    p = OUT + name
    if lossless: im.save(p, "WEBP", lossless=True, quality=100, method=6)
    else: im.save(p, "WEBP", quality=q, alpha_quality=92, method=6)
    print("  ", name, im.size, round(os.path.getsize(p) / 1024), "KB")
def keyed(p, hexkey="FF00FF"):
    out = CACHE + os.path.basename(p)
    if not os.path.exists(out): subprocess.run(["python3", "tools/key_layer.py", p, out, hexkey], check=True)
    return load(out)


# ---------- доска: рамка (9-slice), пол, лунки ----------
FRAME_OUT = 1138    # px: внешний габарит рамки 569 логических x2 (внешний край 32..2016 мастера 2048 = 1984 px)
def board():
    for t in ("day", "night"):
        fr = load(E + f"frame/frame_{t}_thin_fit.png").crop((32, 32, 2016, 2016)); save(sz(fr, FRAME_OUT, FRAME_OUT), f"frame_{t}.webp")
        fl = Image.open(E + f"floor/floor_{t}_v2.png").convert("RGB"); save(sz(fl, 1024, 1024), f"floor_{t}.webp", False, 84)
        sk = keyed(E + ("floor/socket_night_v2.png" if t == "night" else "floor/socket_day_v3_2.png"))
        sk = sk.crop(sk.getchannel("A").point(lambda v: 255 if v > 200 else 0).getbbox())
        cell = Image.new("RGBA", (140, 140), (0, 0, 0, 0)); s = sz(sk, 133, 133); cell.alpha_composite(s, (3, 3))   # лунка 95% клетки, зазор 5%
        save(cell, f"socket_{t}.webp")


# ---------- плитки, здания, капсулы, мини-фон, таблички ----------
def world():
    save(load("out/tiles/sheets/tiles@2x.png"), "tiles.webp")
    save(load(E + "buildings/sheets/buildings@2x.png"), "buildings.webp")
    # жилая линия (павильон-хранилище без задней стенки, tools/open_pavilion.py) отдельным листом: 120x128 логических, x1,2 от слота 100
    hs = Image.new("RGBA", (240, 256 * 4), (0, 0, 0, 0))
    for i, n in enumerate(("shack_1", "house_2", "fort_3", "castle_4")): hs.alpha_composite(sz(load(E + f"buildings/open/{n}.png"), 240, 256), (0, i * 256))
    save(hs, "home.webp")
    # башня магии и кристаллы (gem_1..4, tower_1) отдельным листом x1,5: 120x160 логических, строка = состояние
    ts = Image.new("RGBA", (240, 320 * 5), (0, 0, 0, 0))
    for i, n in enumerate(("gem_1", "gem_2", "gem_3", "gem_4", "tower_1")): ts.alpha_composite(sz(load(E + f"buildings/composed/{n}.png"), 240, 320), (0, i * 320))
    save(ts, "tower.webp")
    for n, h in ((1, 19.0), (2, 29.2), (3, 39.4)):
        save(sz(load(E + f"capsules/composed/capsule_{n}.png"), 152, round(h * 2)), f"capsule_{n}.webp")
    # иконки ресурсов для лунок капсул (спрайт 4 x 24 px, порядок grain stone wood clay cloth)
    names = ["grain_1_v2", "stone_1_v2", "wood_1_v2", "clay_1_v3", "cloth_1_v8"]; sp = Image.new("RGBA", (24 * len(names), 24), (0, 0, 0, 0))
    for i, n in enumerate(names):
        ic = trim(load(f"out/tiles/keyed/{n}.png")); r = 22 / max(ic.size); ic = ic.resize((max(1, round(ic.width * r)), max(1, round(ic.height * r))), Image.LANCZOS)
        sp.alpha_composite(ic, (i * 24 + (24 - ic.width) // 2, (24 - ic.height) // 2))
    save(sp, "capsule_icons.webp")
    for sfx in ("", "_night"):
        save(sz(load(E + f"capsules/composed/ground_tile{sfx}.png"), h=28), f"ground_tile{sfx}.webp")
        for s in ("l", "r"): save(sz(load(E + f"capsules/composed/ground_cap_{s}{sfx}.png"), 44, 28), f"ground_cap_{s}{sfx}.webp")
    for t in ("day", "night"): save(sz(load(E + f"signs/composed/sign_{t}.png"), 88, 168), f"sign_{t}.webp")


# ---------- HUD ----------
THICK = 56          # толщина панелей (логических px)
def hud():
    for t in ("day", "night"):
        pl = trim(load(I + f"panel_plate_{t}_v1.png")); H = pl.height
        h = sz(pl, h=THICK * 2)                                      # горизонтальная плашка, толщина x2
        save(h, f"plate_h_{t}.webp"); save(h.rotate(90, expand=True), f"plate_v_{t}.webp")
        print("   плашка: cap px x2 =", round(120 * THICK * 2 / H, 1), "исх. H", H, "W", pl.width)
        # сердце: гнездо + заливка по центроиду полости (как в mock_all.hearts), холст 96x96
        sock = load(I + f"heart_socket_{t}_v1.png"); S = 96
        save(sz(sock, S, S), f"heart_socket_{t}.webp")
        if t == "day":
            a = np.array(sock); c = (a[..., 0] > 205) & (a[..., 1] > 190) & (a[..., 2] > 150) & (a[..., 3] > 200)
            c = ndi.binary_closing(c, iterations=3); l, n = ndi.label(c)
            hol = ndi.binary_fill_holes(l == (np.argmax(ndi.sum(c, l, range(1, n + 1))) + 1)); hy, hx = np.where(hol); hc = (hx.mean(), hy.mean())
            f = load(I + "heart_fill_v1.png"); f = f.crop(f.getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox())
            fy, fx = np.where(np.array(f.getchannel("A")) > 128); fc = (fx.mean(), fy.mean()); sc = 0.98 * 0.92
            f2 = f.resize((round(f.width * sc), round(f.height * sc)), Image.LANCZOS); fcx, fcy = fc[0] * f2.width / f.width, fc[1] * f2.height / f.height
            cv = Image.new("RGBA", (512, 512), (0, 0, 0, 0)); cv.alpha_composite(f2, (round(hc[0] - fcx), round(hc[1] - fcy)))
            save(sz(cv, S, S), "heart_fill.webp")
            save(sz(f, 88, None), "heart_plain.webp")   # голое сердце без кольца (телефон), 44 логических px в ширину
        # лиана: сегмент + зеркальная копия, повтор по y
        v = trim(load(I + f"vine_wrap_{t}_v1.png")); vh = THICK * 9 * 2; v = sz(v, h=vh); st = Image.new("RGBA", (v.width, vh * 2 - 16), (0, 0, 0, 0))
        st.alpha_composite(v, (0, 0)); st.alpha_composite(v.transpose(Image.FLIP_TOP_BOTTOM), (0, vh - 16)); save(st, f"vine_{t}.webp")
        # кольцо инвентаря (вырезано из планки) и кольцо магии
        pk = trim(load(I + f"inventory_plank_{t}_v1.png")); W_, H_ = pk.size; cx, cy, r = int(W_ * 0.495), H_ // 2, int(H_ * 0.44)
        ring = pk.crop((cx - r, cy - r, cx + r, cy + r)); m = Image.new("L", ring.size, 0); ImageDraw.Draw(m).ellipse([0, 0, ring.width - 1, ring.height - 1], fill=255)
        ring.putalpha(ImageChops.multiply(ring.getchannel("A"), m)); save(sz(ring, 144, 144), f"ring_{t}.webp")
        rg = sz(trim(load(I + f"slot_ring_{t}_v1.png")), 256, None); save(rg, f"slot_{t}.webp")
        # кольцо маны с прозрачным отверстием (заливка маны лежит под ним): эллипс по замеру дневного кольца (центр 125;120,5, полуоси 94;92 из 256x261), одинаков для дня и ночи
        a = np.array(rg); H, W = a.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
        hole = ((xx - 125) / 94.0) ** 2 + ((yy - 120.5) / 92.0) ** 2 < 1
        al = a[..., 3].astype(float) * (1 - ndi.gaussian_filter(hole.astype(float), 1.0)); a[..., 3] = al.clip(0, 255).astype(np.uint8)
        save(Image.fromarray(a), f"mana_ring_{t}.webp")
    for n in ("bomb", "dragon_scroll", "equipment", "health_potion", "mana_potion"): save(sz(trim(load(I + f"loot_{n}_v1.png")), 96, 96) if False else sz(load(I + f"loot_{n}_v{2 if n == 'equipment' else 1}.png"), 144, 144), f"loot_{n}.webp")
    # щит (дерево) и меч (камень): иконки ночных плиток по уровням 1..9 (те же, что в плитках), спрайт 9 x 60 px (x2 от 30)
    KN = "out/tiles/keyed-night/"; NV = {"stone_2": 5, "stone_3": 3, "wood_2": 2, "wood_3": 2}
    for cls, nm in (("wood", "shield"), ("stone", "sword")):
        sp = Image.new("RGBA", (60, 60 * 9), (0, 0, 0, 0))
        for l in range(1, 10):
            f = KN + ("stone_1_v2" if (cls, l) == ("stone", 1) else f"{cls}_{l}_v{NV.get(f'{cls}_{l}', 1)}") + ".png"
            ic = trim(load(f)); r = 56 / max(ic.size); ic = ic.resize((round(ic.width * r), round(ic.height * r)), Image.LANCZOS)
            sp.alpha_composite(ic, ((60 - ic.width) // 2, (l - 1) * 60 + (60 - ic.height) // 2))
        save(sp, f"gear_{nm}.webp")
    for n in ("freeze_time", "haste", "phase_change"): save(sz(load(I + f"spell_{n}_v1.png"), 160, 160), f"spell_{n}.webp")


# ---------- фоны: 4 этапа x день/ночь x land/port x far/mid + передний план ----------
def _bg_one(job):
    src, dst, key, w = job
    if os.path.exists(OUT + dst): return dst
    im = keyed(src) if key else load(src)
    im = sz(im, w, None)
    if key or im.getchannel("A").getextrema()[0] < 255: im.save(OUT + dst, "WEBP", quality=86, alpha_quality=90, method=6)
    else: im.convert("RGB").save(OUT + dst, "WEBP", quality=82, method=6)
    return dst

def bg():
    jobs = []
    for s in (1, 2, 3, 4):
        for t in ("day", "night"):
            jobs += [(E + f"bg/bg_s{s}_far_{t}_land_v1.png", f"bg/s{s}_far_{t}_land.webp", False, 2400),
                     (E + f"bg/bg_s{s}_mid_{t}_land_v1.png", f"bg/s{s}_mid_{t}_land.webp", True, 2400),
                     (E + f"bg/bg_s{s}_far_{t}_port_v1.png", f"bg/s{s}_far_{t}_port.webp", False, 1080),
                     (E + f"bg/bg_s{s}_mid_{t}_port_" + ("v2" if (s == 3 and t == "day") else "v1") + ".png", f"bg/s{s}_mid_{t}_port.webp", False, 1080)]
    jobs += [(E + "fg/fg_day_land_v3.png", "bg/fg_day_land.webp", False, 2400), (E + "fg/fg_night_land_v2.png", "bg/fg_night_land.webp", False, 2400),
             (E + "fg/fg_day_port_v4_a.png", "bg/fg_day_port.webp", False, 1080), (E + "fg/fg_night_port_v3_a.png", "bg/fg_night_port.webp", False, 1080)]
    for a_, w_ in (("land", 2400), ("port", 1080)):   # бой с драконом: far opaque, mid и fg по ключу
        jobs += [(E + f"bg/bg_dragon_far_{a_}_v1.png", f"bg/dragon_far_{a_}.webp", False, w_),
                 (E + f"bg/bg_dragon_mid_{a_}_v1.png", f"bg/dragon_mid_{a_}.webp", True, w_),
                 (E + f"fg/fg_dragon_{a_}_v1.png", f"bg/dragon_fg_{a_}.webp", True, w_)]
    with ProcessPoolExecutor(4) as ex:
        for d in ex.map(_bg_one, jobs): print("  ", d, round(os.path.getsize(OUT + d) / 1024), "KB")


# ---------- сгенерированный CSS: фоны по этапам и раскладка запаса ----------
def css():
    import json
    D = lambda a, b, s: f"url(../img/v2/bg/s{s}_{a}_{b}"
    out = ["/* Генерируется rebranding/tools/export_www.py (css). Не править руками. */"]
    for aspect in ("land", "port"):
        rules = []
        for s in (1, 2, 3, 4):
            for layer in ("far", "mid"):
                for t in ("day", "night"):
                    rules.append(f".stage{s} #bg .{layer}.{t} {{ background-image: url(../img/v2/bg/s{s}_{layer}_{t}_{aspect}.webp); }}")
        for t in ("day", "night"): rules.append(f"#fg .{t} {{ background-image: url(../img/v2/bg/fg_{t}_{aspect}.webp); }}")
        rules += [f"#bg .far.drbg {{ background-image: url(../img/v2/bg/dragon_far_{aspect}.webp); }}", f"#bg .mid.drbg {{ background-image: url(../img/v2/bg/dragon_mid_{aspect}.webp); }}",
                  f"#fg .drbg {{ background-image: url(../img/v2/bg/dragon_fg_{aspect}.webp); }}"]
        out.append("\n".join(rules) if aspect == "land" else "@media (max-aspect-ratio: 1/1) {\n" + "\n".join(rules) + "\n}")
    open("../www/css/bg.css", "w").write("\n".join(out) + "\n")
    lay = json.load(open("store-layout.json")); c = lay["cell"]
    o = ["/* Генерируется rebranding/tools/export_www.py (css) из store-layout.json: ячейки запаса по стадиям жилой линии (px кадра спрайта 100x106,7). */"]
    Z = 1.2   # спрайт жилой линии увеличен x1,2 (слот 120)
    for pre, name in (("", "shack_1"), (".grain2", "house_2"), (".grain3", "fort_3"), (".grain4", "castle_4")):
        for i, (x, y) in enumerate(lay["stages"][name]["cells"]):
            o.append(f"{pre} .resources .block:nth-child({i + 1}) {{ left: {x * Z:.2f}px; top: {y * Z:.2f}px; }}".strip())
    open("../www/css/store.css", "w").write("\n".join(o) + f"\n.resources .block {{ width: {c * Z:g}px; height: {c * Z:g}px; }}\n")


# ---------- сессия 6: остальные иконки (reset_board, frozen, золотые сердца, солнце/луна) ----------
def icons2():
    for n, src in (("spell_reset_board", "out/icons/spells/spell_reset_board_v1.png"), ("state_frozen", "out/icons/spells/state_frozen_v1.png")):
        save(sz(keyed(src), 160, 160), n + ".webp")
    S = 96
    for t in ("day", "night"): save(sz(keyed(f"out/icons/hud/heartbig_socket_{t}_v1.png"), S, S), f"heartbig_socket_{t}.webp")
    # золотая заливка по центроиду полости дневного гнезда (как для красного сердца в hud())
    a = np.array(keyed("out/icons/hud/heartbig_socket_day_v1.png")); c = (a[..., 0] > 205) & (a[..., 1] > 190) & (a[..., 2] > 150) & (a[..., 3] > 200)
    c = ndi.binary_closing(c, iterations=3); l, n = ndi.label(c)
    hol = ndi.binary_fill_holes(l == (np.argmax(ndi.sum(c, l, range(1, n + 1))) + 1)); hy, hx = np.where(hol); hc = (hx.mean(), hy.mean())
    f = keyed("out/icons/hud/heartbig_fill_v1.png"); f = f.crop(f.getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox())
    fy, fx = np.where(np.array(f.getchannel("A")) > 128); fc = (fx.mean(), fy.mean()); sc = 0.98 * 0.92
    f2 = f.resize((round(f.width * sc), round(f.height * sc)), Image.LANCZOS); fcx, fcy = fc[0] * f2.width / f.width, fc[1] * f2.height / f.height
    cv = Image.new("RGBA", (512, 512), (0, 0, 0, 0)); cv.alpha_composite(f2, (round(hc[0] - fcx), round(hc[1] - fcy)))
    save(sz(cv, S, S), "heartbig_fill.webp"); save(sz(f, 88, None), "heartbig_plain.webp")
    def bake_glow(disc, color, canvas=900, target=128, r_frac=0.33, peak=0.85):
        bb = disc.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox(); disc = disc.crop(bb)
        sc = (canvas * 0.46) / max(disc.size); disc = disc.resize((round(disc.width * sc), round(disc.height * sc)), Image.LANCZOS)
        yy, xx = np.mgrid[0:canvas, 0:canvas]; d = np.sqrt((xx - canvas / 2) ** 2 + (yy - canvas / 2) ** 2)
        a = (np.clip(1 - (d / (canvas * r_frac)) ** 2, 0, 1) ** 1.4 * peak * 255).astype(np.uint8)
        glow = np.zeros((canvas, canvas, 4), np.uint8); glow[..., 0], glow[..., 1], glow[..., 2], glow[..., 3] = color[0], color[1], color[2], a
        cv = Image.fromarray(glow, "RGBA"); cv.alpha_composite(disc, ((canvas - disc.width) // 2, (canvas - disc.height) // 2))
        return cv.resize((target, target), Image.LANCZOS)
    # свечение запечено в альфу картинки (не CSS drop-shadow): не обрезается краем .world при zenith/краях дуги
    save(bake_glow(keyed("out/env/sky/sky_sun_v1.png"), (255, 214, 96)), "sky_sun.webp")
    save(bake_glow(keyed("out/env/sky/sky_moon_v1.png"), (185, 205, 255)), "sky_moon.webp")


# ---------- эмблема: значок игры (badge.png, favicon.ico) и титульный лист (title.png) ----------
def brand():
    from PIL import ImageFont, ImageFilter
    em = trim(keyed("out/icons/brand/logo_emblem_v2.png"))
    # значок: скруглённый квадрат цвета песка с деревянным кантом, эмблема с полями (250 px = x2 от 125)
    W = 250; bd = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(bd)
    d.rounded_rectangle([0, 0, W - 1, W - 1], 44, fill=(124, 82, 48, 255)); d.rounded_rectangle([9, 9, W - 10, W - 10], 36, fill=(238, 220, 178, 255))
    e = em.copy(); e.thumbnail((W - 60, W - 60), Image.LANCZOS); bd.alpha_composite(e, ((W - e.width) // 2, (W - e.height) // 2))
    bd.save("../www/img/badge.png"); bd.resize((48, 48), Image.LANCZOS).save("../www/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    # титульный лист 1200x334 (x2 от 600x167): эмблема слева, слово MATCHHOLD справа (шрифт из системы, временный)
    T = Image.new("RGBA", (1200, 334), (0, 0, 0, 0)); e2 = em.copy(); e2.thumbnail((300, 310), Image.LANCZOS); T.alpha_composite(e2, (20, (334 - e2.height) // 2))
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", 108); txt = "MATCHHOLD"
    mk = Image.new("L", T.size, 0); ImageDraw.Draw(mk).text((350, 167), txt, font=font, fill=255, anchor="lm", stroke_width=0)
    bb = mk.getbbox(); sh = Image.new("RGBA", T.size, (0, 0, 0, 0))
    sh.paste((92, 58, 30, 255), mask=mk.filter(ImageFilter.MaxFilter(11)))
    sh2 = Image.new("RGBA", T.size, (0, 0, 0, 0)); sh2.paste((0, 0, 0, 70), mask=ImageChops.offset(mk.filter(ImageFilter.MaxFilter(11)), 5, 6).filter(ImageFilter.GaussianBlur(3)))
    gold = Image.new("RGBA", T.size, (0, 0, 0, 0)); g = Image.new("RGBA", T.size)
    for y in range(T.height): ImageDraw.Draw(g).line([(0, y), (T.width, y)], fill=(255, 214 - y // 6, 96 - y // 8, 255))
    gold.paste(g, mask=mk); T.alpha_composite(sh2); T.alpha_composite(sh); T.alpha_composite(gold)
    print("   title bbox", bb); T.save("../www/img/title.png")


# ---------- сессия 10: снаряды и боевые эффекты (стрела, огненный/тёмный снаряд, вспышка, шары луча, огонь, лёд) ----------
def fx():
    F = "out/fx/"; os.makedirs(OUT + "fx", exist_ok=True)
    def strip(name, w, key):   # полоса 2 кадра: остриё влево | остриё вправо (исходник смотрит вправо)
        a = trim(keyed(F + name + "_v1.png", key)); a = sz(a, w * 3); h = a.height
        s = Image.new("RGBA", (a.width * 2, h), (0, 0, 0, 0)); s.alpha_composite(a.transpose(Image.FLIP_LEFT_RIGHT), (0, 0)); s.alpha_composite(a, (a.width, 0))
        save(s, f"fx/{name}.webp"); print("    cell css", w, "x", round(h / 3, 1))
    strip("arrow", 32, "FF00FF"); strip("firebolt", 28, "00FF00"); strip("arcane", 28, "00FF00")
    save(sz(trim(keyed(F + "burst_v1.png", "00FF00")), 256), "fx/burst.webp")
    save(sz(trim(keyed(F + "orb_fire_v1.png", "00FF00")), 96), "fx/orb_fire.webp")
    save(sz(trim(keyed(F + "orb_ice_v1.png", "FF00FF")), 96), "fx/orb_ice.webp")
    # лист эффектов на земле: 120x176 логич. (сверху 88 пустых под смещение dragoneffects), ряд 0 лёд (1 кадр), ряд 1 огонь (4 кадра), кадр 30x44
    W, H = 90, 132; sheet = Image.new("RGBA", (W * 4, 528), (0, 0, 0, 0))
    ia = sz(trim(keyed(F + "iceblock_v1.png", "FF00FF")), h=124)
    sheet.alpha_composite(ia, ((W - ia.width) // 2, 264 + H - 4 - ia.height))
    fl = keyed(F + "flames_v1.png", "00FF00"); cells = [trim(fl.crop((x, y, x + 512, y + 512))) for y in (0, 512) for x in (0, 512)]
    k = 124 / max(c.height for c in cells)
    for i, c in enumerate(cells):
        c = c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS); sheet.alpha_composite(c, (i * W + (W - c.width) // 2, 396 + H - 4 - c.height))
    save(sheet, "fx/effects.webp")


if __name__ == "__main__":
    groups = sys.argv[1:] or ["board", "tiles", "world", "hud", "icons2", "brand", "bg", "css"]
    for g in groups:
        print("==", g); {"board": board, "tiles": world, "world": world, "hud": hud, "icons2": icons2, "brand": brand, "fx": fx, "bg": bg, "css": css}[g]()

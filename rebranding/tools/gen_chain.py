"""Цепочка стадий зданий (сессия 4): каждая стадия генерируется по предыдущей (реф #1 = предыдущая стадия с альфой, реф #2 = ref_row).
Автопроверка после ключа: края L/R/T прозрачны, прозрачно >15%; при провале одна повторная попытка (v+1).
Запуск из rebranding/: python3 tools/gen_chain.py <линия> ; линии: home bricklayer weaver blacksmith sawmill gem.  Результат: out/env/buildings/<id>_v<N>.png, keyed/, chain_<линия>.json"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image

B = "out/env/buildings/"
TAG = os.environ.get("TAG", "v")   # тег попытки в имени файла: <id>_<TAG><N>.png
S = os.environ.get("S", "/tmp/claude-1000/-home-user-projects-matchhold/8cf97f12-1c34-4a07-9e32-fb51c227da2b/scratchpad")
DAY = ("Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine, NO glassy sparkle. "
       "Warm afternoon light from the top-left, soft warm shadow toward the bottom-right. A thin outline slightly darker than the object own hue (about 2-3% of the object size), never black. Clean, readable silhouette. "
       "Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.")
NEG = ("Avoid: people, characters, text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage, "
       "cast shadow on the ground, ground plane, grass, trees, background scenery.")
TPL = ("One single building only. Front three-quarter view, standing on flat ground, the ground line is the bottom of the building (its base touches the bottom of the subject), centered, "
       "fills about 80% of the canvas width and 86% of the height, with clear empty margins on the left, right and top. Matte, no gloss.")
UP = "Same architecture, camera angle, materials, scale and colour palette as the FIRST attached image (the previous stage of this building series), but "
EMPTY = " IMPORTANT: leave the space under the canopy completely EMPTY (no crates, barrels, sacks, shelves or tools), the floor and the back wall must stay visible."
GEM = ("One single small object only. Front three-quarter view, centered, its base touches the bottom of the subject, fills about 60% of the canvas width and 55% of the height. Matte, no gloss.")

# линия: (ключ фона, первая стадия: файл без .png, [(id, текст)]).
HV = {"A": ("the pavilion is TALL, like an open-fronted barn: its posts are TWICE as tall as the door of the small house on the right, so under the horizontal beam there is a tall clear rectangular opening "
                "(taller than the door of the house by a factor of two, and about 60% as wide as the whole building), the roof is high above it"),
      "B": ("the pavilion is a tall open hall, almost as tall as it is wide (aspect about 1:1.1), with very tall slim posts, a tall clear rectangular opening under the horizontal beam that takes more than 40% of the total height of the building, "
                "and a compact low roof on top"),
      "": "the clear rectangular opening between the posts (floor to the horizontal beam) is at least {W}% of the building width and {H}% of the building height"}[os.environ.get("HV", "")]
HALL = (" a storehouse: on the left about 68% of the width a wide open-fronted timber pavilion seen with its LONG side facing the viewer (NOT the gable end): a shingle roof carried by four thick posts and a straight horizontal beam across the front, "
        "the front completely open between the posts, a plank floor, the back wall visible; " + HV + " and completely EMPTY "
        "(no crates, barrels, sacks, shelves or tools, no diagonal braces or trusses inside the opening); and on the right about 28% of the width {RIGHT}.")
LINES = {
 "hall": ("FF00FF", None, [
   ("shack_1", "Subject:" + HALL.format(RIGHT="a small cosy timber-framed house with a honey-gold thatched roof, a door and a chimney", W=55, H=42)),
   ("house_2", UP + "bigger and TALLER (the pavilion posts about 30% taller than in the previous stage, the clear opening about 30% larger):" + HALL.format(RIGHT="the timber-framed house with a red tile roof, a small window with a flower box", W=58, H=48)),
   ("fort_3", UP + "sturdier, fortified, and TALLER again (posts about 30% taller than in the previous stage, the clear opening larger, at least 1.3 times as tall as the door of the house):" + HALL.format(RIGHT="the house on a stone base with a small wooden watch platform with a pennant and a low wooden palisade behind", W=62, H=50)),
   ("castle_4", UP + "a small stone castle, and the pavilion is the TALLEST yet (posts about 30% taller than in the previous stage, a very tall clear opening, at least 1.6 times as tall as the door of the house):" + HALL.format(RIGHT="a stone keep with two round towers rising behind the pavilion corner, crenellations, a gate and a blue banner", W=68, H=50))]),
 "home": ("FF00FF", "store_1_v1", [
   ("house_2", UP + "bigger: the timber-framed house with a red tile roof, a second small window and a flower box; the open canopy on the left is larger and deeper (about 55% of the width), still with an empty wooden plank floor." + EMPTY),
   ("fort_3", UP + "sturdier and fortified: stone base, a small wooden watch platform with a pennant on the house, a low wooden palisade fence along the back; the open canopy on the left is even larger with a stone-footed frame." + EMPTY),
   ("castle_4", UP + "a small stone castle: on the right a stone keep with two round towers, crenellations, a gate and a blue banner; on the left a large open vaulted stone-and-timber hall with a wide empty floor." + EMPTY)]),
 "bricklayer": ("FF00FF", "bricklayer_1_v3", [
   ("bricklayer_2", UP + "a small brick kiln with a little smoke and a few stacked bricks (the clay pit and shed become a proper kiln building)."),
   ("bricklayer_3", UP + "a larger brick kiln, stacked brick pallets beside it, more smoke."),
   ("bricklayer_4", UP + "a brick workshop with a tall chimney, a finished brick wall segment and a wheelbarrow.")]),
 "weaver": ("00FF00", "weaver_1_v1", [
   ("weaver_2", UP + "bigger: a weaver's stall with a cream-and-lavender striped awning, rolls of violet fabric on a table beside the loom."),
   ("weaver_3", UP + "a weaver's house with two looms and dyed violet fabrics hanging on a line."),
   ("weaver_4", UP + "a grand weaver's hall with violet and gold banners and rich fabric bolts on display.")]),
 "blacksmith": ("FF00FF", "blacksmith_1_v3", [
   ("blacksmith_2", UP + "a wider forge, a second chimney and a small weapon rack."),
   ("blacksmith_3", UP + "a two-bay forge with bellows and several steel swords displayed."),
   ("blacksmith_4", UP + "a dark stone forge with a red-hot furnace glow at the door, same layout as the previous stage."),
   ("blacksmith_5", UP + "bigger, orange fire glow spilling from the windows, a few sparks."),
   ("blacksmith_6", UP + "the largest fire-tier forge, a flaming sword sign, strong glow."),
   ("blacksmith_7", UP + "a frost-tier forge: pale blue stone, blue cold flame glow, icicles on the roof."),
   ("blacksmith_8", UP + "a grand ice-steel forge with gold trim and the brightest cold glow.")]),
 "sawmill": ("FF00FF", "sawmill_1_v3", [
   ("sawmill_2", UP + "a bigger shed, a plank stack and a small water wheel."),
   ("sawmill_3", UP + "a two-bay sawmill, a larger water wheel, more planks."),
   ("sawmill_4", UP + "a dark hardwood sawmill, same layout as the previous stage, darker timber."),
   ("sawmill_5", UP + "larger, with a second floor and stacked dark planks."),
   ("sawmill_6", UP + "the largest dark-tier sawmill, a big wheel, a wide plank yard."),
   ("sawmill_7", UP + "golden-trimmed timber, a faint magical green leaf glow and a few sparkling leaves."),
   ("sawmill_8", UP + "a grand gilded sawmill, the brightest glow, a golden wheel.")]),
 "gem": ("00FF00", None, [
   ("gem_1", "A small round grey-beige stone pedestal with ONE glowing pink-magenta mana crystal on top."),
   ("gem_2", UP + "the same pedestal (identical) with TWO glowing pink-magenta mana crystals."),
   ("gem_3", UP + "the same pedestal (identical) with THREE glowing pink-magenta mana crystals."),
   ("gem_4", UP + "the same pedestal (identical) with FOUR glowing pink-magenta mana crystals.")]),
}

def key(name, hexk):
    os.makedirs(B + "keyed", exist_ok=True); k = f"{B}keyed/{name}.png"
    if not os.path.exists(k): subprocess.run(["python3", "tools/key_layer.py", f"{B}{name}.png", k, hexk], check=True, capture_output=True)
    return k

def ok(k):
    a = np.array(Image.open(k).convert("RGBA"))[..., 3]
    return bool(a[:, 0].max() < 20 and a[:, -1].max() < 20 and a[0].max() < 20 and (a < 10).mean() > 0.15)

def codex(name, refs, hexk, prompt, tpl):
    out = f"{B}{name}.png"
    if os.path.exists(out): return
    p = (f"Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them for style, palette, material and level of detail, and where the prompt says, for the architecture. "
         f"Target size 768x1024 (if the native size differs, resize the whole picture to FIT INSIDE that size with ImageMagick and pad the rest with the key colour; NEVER crop, NEVER stretch; the building must stay complete, "
         f"with at least 6% of empty key-colour margin on every side). PNG. {DAY} {tpl} {prompt} The whole background is a solid flat #{hexk} (no gradient, no shadow, no fringe); nothing in the artwork is that colour. {NEG} "
         f"Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/{out} . Do not overwrite existing files. Print the saved path and dimensions.")
    subprocess.run(["codex", "exec", "-m", "gpt-5.6-terra", "-c", "model_reasoning_effort=low", "--sandbox", "workspace-write", p, "-i", *refs],
                   stdout=open(f"{S}/{name}.log", "w"), stderr=subprocess.STDOUT)

if __name__ == "__main__":
    line = sys.argv[1]; hexk, first, stages = LINES[line]; prev = os.environ.get("PREV") or first; res = {}
    R = B + "ref_row.png"
    only = os.environ.get("ONLY"); stages = [x for x in stages if not only or x[0] in only.split(",")]
    for sid, text in stages:
        for att in (1, 2):
            name = f"{sid}_{TAG}{att}"
            refs = ([key(prev, hexk)] if prev else []) + [R]
            if line == "gem" and sid == "gem_1": refs = [R, B + "keyed/blacksmith_1_v3.png"]
            codex(name, refs, hexk, text, GEM if line == "gem" else TPL)
            if not os.path.exists(f"{B}{name}.png"): res[sid] = {"file": None, "ok": False}; continue
            good = ok(key(name, hexk)); res[sid] = {"file": name, "ok": good}
            if good: break
        prev = res[sid]["file"] or prev
        json.dump(res, open(f"{B}chain_{line}.json", "w"), indent=1)
    print(line, "DONE", json.dumps(res))

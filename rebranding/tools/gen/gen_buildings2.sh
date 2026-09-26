#!/bin/bash
# Гейт 2b, правки пользователя: (1) жилая линия = дом-хранилище с большим пустым навесом (под навесом игра рисует запас),
# (2) башня магии: витиеватая остроконечная, (3) капсулы: каменный фундамент вместо дерева (та же раскладка, что capsule_3_v1).
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/8cf97f12-1c34-4a07-9e32-fb51c227da2b/scratchpad}
mkdir -p "$S"
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine, NO glassy sparkle. Warm afternoon light from the top-left, soft warm shadow toward the bottom-right. A thin outline slightly darker than the object own hue (about 2-3% of the object size), never black. Clean, readable silhouette. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NEG='Avoid: people, characters, text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage, cast shadow on the ground, ground plane, grass, trees, background scenery.'
gen() { # out refs size key prompt
  [ -f "$1" ] && return
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them for style, palette, material and level of detail only, do not copy their composition. Target size $3 (if the native size differs, resize the whole picture to FIT INSIDE that size with ImageMagick and pad the rest with the key colour; NEVER crop, NEVER stretch; the whole subject must stay complete, with at least 6% of empty key-colour margin on every side). PNG. $5 The whole background is a solid flat $4 (no gradient, no shadow, no fringe); nothing in the artwork is that colour. $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
R=out/env/buildings/ref_row.png; A=out/env/buildings/blacksmith_1_v3.png; B=out/env/buildings
TPL='One single building only. Front three-quarter view, standing on flat ground, the base touches the bottom of the subject, centered, fills about 80% of the canvas width and 86% of the height. Matte, no gloss.'
for v in 1 2; do
gen $B/store_1_v$v.png "$R $A" 768x1024 '#FF00FF' "$DAY $TPL Subject: a storehouse. On the right about 45% of the width a small cosy timber-framed house with a honey-gold thatched roof, a door and a chimney. On the left about 55% of the width a big open-sided timber lean-to canopy (a sloped shingle roof on thick posts, open at the front and the left side) with a plain empty wooden plank floor under it: a wide clear open space to keep goods. IMPORTANT: leave the space under the canopy completely EMPTY (no crates, barrels, sacks, shelves or tools), the floor and the back wall must be visible." &
gen $B/tower_2_v$v.png "$R $A" 768x1024 '#FF00FF' "$DAY $TPL Subject: an ornate MAGIC wizard tower, tall and slender (fills 96% of the height and about 60% of the width), NOT a military watch tower: pale cream stone body with gold spiral scrollwork, two or three stacked tiers each a bit narrower, pointed arched windows with a warm glow, a small curved balcony, and a very tall pointed twisting spire roof of violet-blue shingles with a curled tip and a golden crescent moon finial; two or three small floating pink-magenta mana crystals orbit near the top; whimsical, elegant and curvy, no battlements, no flag." &
done
CAP='A horizontal resource progress capsule frame seen straight from the front, 3 segments stacked vertically, EXACTLY the same layout, proportions and positions as the first attached image (round empty socket on the left, a long empty pill-shaped trough to the right, in each of the 3 rows), but the chestnut wood is replaced by warm grey-beige stone masonry (rectangular cut stone blocks with mortar lines, chunky and rounded, a slightly darker stone ledge at the bottom edge, like a stone foundation plinth), keeping the thin brass rims around the sockets and troughs and the brass corner plates and tiny rivets. The insides of sockets and troughs are dark warm brown recessed, empty: no fill, no icon, no text. No moss, no plants. Matte, no gloss. The capsule fills the canvas edge to edge horizontally with a small margin, exactly one capsule.'
for v in 1 2; do gen out/env/capsules/capsule_stone3_v$v.png out/env/capsules/capsule_3_v1.png 1120x600 '#00FF00' "$DAY $CAP" & done
wait
echo DONE

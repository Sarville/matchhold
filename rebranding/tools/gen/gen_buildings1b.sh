#!/bin/bash
# Гейт 2b, повтор: v1 срезал края cover-кропом (shack, bricklayer, blacksmith, sawmill). Здание вписывается целиком с полем 6% и добивается ключом, без кропа.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/8cf97f12-1c34-4a07-9e32-fb51c227da2b/scratchpad}
mkdir -p "$S"
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine, NO glassy sparkle. Warm afternoon light from the top-left, soft warm shadow toward the bottom-right. A thin outline slightly darker than the object own hue (about 2-3% of the object size), never black. Clean, readable silhouette. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NEG='Avoid: people, characters, text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage, cast shadow on the ground, ground plane, grass, trees, background scenery.'
gen() { # out refs size key prompt
  [ -f "$1" ] && return  # готовые пропускаем
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them for style, palette, material and level of detail only, do not copy their composition. Target size $3 (if the native size differs, resize the whole picture to FIT INSIDE that size with ImageMagick and pad the rest with the key colour; NEVER crop, NEVER stretch; the building must stay complete, with at least 6% of empty key-colour margin on every side). PNG. $5 The whole background is a solid flat $4 (no gradient, no shadow, no fringe); nothing in the artwork is that colour. $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
R=out/env/buildings/ref_row.png
B=out/env/buildings
TPL='One single building only. Front three-quarter view, standing on flat ground, the ground line is the bottom edge of the canvas (the base of the building touches the bottom edge), centered, fills about 80% of the canvas width and 86% of the height, with clear empty margins on the left, right and top. Matte, no gloss.'
b() { # id key subject
  for v in 3 4; do gen $B/$1_v$v.png $R 768x1024 "$2" "$DAY $TPL Subject: $3" & done
}
b shack_1      '#FF00FF' 'small thatched-roof wooden hut with a stone base, one wooden door, one tiny stone chimney, honey-gold straw roof'
b bricklayer_1 '#FF00FF' 'a clay pit with a small wooden shed and a heap of raw terracotta clay and a few loose bricks'
b blacksmith_1 '#FF00FF' 'small stone forge with a slate roof, a stone chimney, an arched fire opening and an iron anvil in front'
b sawmill_1    '#FF00FF' 'small open log shed with a hand saw, a log pile and a few planks'
wait
echo DONE

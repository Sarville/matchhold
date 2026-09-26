#!/bin/bash
# Гейт 2b: первые 6 зданий (по одному на линию, 2 варианта) + 3 капсулы стройки. Здания 768x1024, капсулы 1120x(280|440|600).
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/8cf97f12-1c34-4a07-9e32-fb51c227da2b/scratchpad}
mkdir -p "$S"
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine, NO glassy sparkle. Warm afternoon light from the top-left, soft warm shadow toward the bottom-right. A thin outline slightly darker than the object own hue (about 2-3% of the object size), never black. Clean, readable silhouette. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NEG='Avoid: people, characters, text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage, cast shadow on the ground, ground plane, grass, trees, background scenery.'
gen() { # out refs size key prompt
  [ -f "$1" ] && return  # готовые пропускаем
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them for style, palette, material and level of detail only, do not copy their composition. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $5 The whole background is a solid flat $4 (no gradient, no shadow, no fringe); nothing in the artwork is that colour. $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
R=out/env/buildings/ref_row.png
B=out/env/buildings
TPL='One single building only. Front three-quarter view, standing on flat ground, the ground line is the bottom edge of the canvas (the base of the building touches the bottom edge), centered, fills about 90% of the canvas width and 94% of the height. Matte, no gloss.'
b() { # id key subject
  for v in 1 2; do gen $B/$1_v$v.png $R 768x1024 "$2" "$DAY $TPL Subject: $3" & done
}
b shack_1      '#FF00FF' 'small thatched-roof wooden hut with a stone base, one wooden door, one tiny stone chimney, honey-gold straw roof'
b bricklayer_1 '#FF00FF' 'a clay pit with a small wooden shed and a heap of raw terracotta clay and a few loose bricks'
b weaver_1     '#00FF00' 'tiny wooden lean-to with a simple loom and a hanging cream-and-lavender cloth'
b blacksmith_1 '#FF00FF' 'small stone forge with a slate roof, a stone chimney, an arched fire opening and an iron anvil in front'
b sawmill_1    '#FF00FF' 'small open log shed with a hand saw, a log pile and a few planks'
b tower_1      '#FF00FF' 'round stone watch tower with a slate cone roof and a blue banner with a golden fleur-de-lis, small wooden door'
CAP='A horizontal resource progress capsule frame seen straight from the front, {N} segment(s) stacked vertically. Each segment: a round empty socket on the left (for an icon) and a long empty rounded pill-shaped trough to the right, dark warm brown inset interior, framed in warm chestnut wood with a thin brass rim and tiny brass rivets. Empty inside: no fill, no icon, no text. Slight inner shadow at the top of the trough. Matte, no gloss. The capsule fills the canvas edge to edge horizontally with a small margin, exactly one capsule.'
P=out/icons/hud/panel_plate_day_v1.png
c() { gen out/env/capsules/capsule_$1_v1.png "$P" $3 '#00FF00' "$DAY ${CAP//\{N\}/$2}" & }
c 1 1 1120x280
c 2 2 1120x440
c 3 3 1120x600
wait
echo DONE

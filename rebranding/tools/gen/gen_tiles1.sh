#!/bin/bash
# T0 плашки (день/ночь) + T1 дневные якорные иконки, по 3 варианта. Гейт 1 после этого.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/1c0c8486-b0b8-4f15-b3c1-7e302a3138b4/scratchpad}
mkdir -p "$S"
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine, NO glassy sparkle. Warm afternoon light from the top-left, soft warm shadow toward the bottom-right. A thin outline slightly darker than the object own hue (about 2-3% of the object size), never black. Clean, readable silhouette. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light. Thin outline slightly darker than the object own hue, never black.'
KEY='The whole background is a solid flat #FF00FF (no gradient, no shadow, no fringe); nothing else in the artwork is pink or magenta. One object only, centered, no ground shadow, no text.'
KEYMANA='The whole background is a solid flat #00FF00 (no gradient, no shadow, no fringe); nothing else in the artwork is green. One object only, centered, no ground shadow, no text.'
NEG='Avoid: text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage.'
gen() { # out refs size key prompt
  [ -f "$1" ] && return  # уже есть: перезапуск доделывает только недостающее
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them where the prompt says, otherwise use them for style, palette and material only. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $5 $4 $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
D=refs/ref-day-tiles.png; N=refs/ref-night-tiles.png
T=out/tiles
PD="$DAY One square game tile plate, seen straight from the front, slightly raised like a soft stone-and-clay tile, rounded corners (radius about 14% of the side), exactly like the plain tile plates in the attached reference but with the icon removed. Warm cream-beige face (#EFE3CC) with a very soft matte gradient, a subtle lighter bevel along the top and left edges, a slightly darker warm-beige edge along the bottom and right, a thin outline a little darker than the face. No icon, no pattern, no text, no gloss, NO cast shadow outside the plate. The plate fills 88% of a square 512x512 canvas."
PN="$NIGHT One square game tile plate, seen straight from the front, slightly raised, rounded corners (radius about 14% of the side), exactly like the plain tile plates in the second attached reference but with the icon removed, and with the same shape and proportions as in the first attached image. Deep navy-slate face (#2E3853) with a very soft matte gradient, a faint cool moonlit rim light along the top and left edges, a darker navy edge along the bottom and right, a thin outline a little darker than the face. No icon, no pattern, no text, no gloss, NO cast shadow outside the plate. The plate fills 88% of a square 512x512 canvas."
IC='A single game tile icon, three-quarter view from above, centered, fills about 66% of the canvas, no plate, no frame, no ground shadow, readable at 52 px, same outline weight and lighting as the attached reference tiles.'
for v in 1 2 3; do
  gen $T/plate/plate_day_v$v.png $D 512x512 "$KEY" "$PD" &
  gen $T/plate/plate_night_v$v.png "$D $N" 512x512 "$KEY" "$PN" &
done
wait
for v in 1 2 3; do
  gen $T/anchors/grain_1_v$v.png $D 512x512 "$KEY" "$DAY $IC Subject: a golden wheat sheaf tied with a rope, plump grains, as in the reference. Palette: honey gold." &
  gen $T/anchors/wood_1_v$v.png $D 512x512 "$KEY" "$DAY $IC Subject: two stacked chestnut logs with visible round ends and rings, as in the reference. Palette: chestnut brown." &
  gen $T/anchors/stone_1_v$v.png $D 512x512 "$KEY" "$DAY $IC Subject: a rough faceted grey stone block, cool grey with lighter top facets, as in the reference. Palette: cool grey." &
done
wait
for v in 1 2 3; do
  gen $T/anchors/clay_1_v$v.png $D 512x512 "$KEY" "$DAY $IC Subject: a rough lump of raw terracotta clay with a couple of finger marks. Palette: terracotta red." &
  gen $T/anchors/cloth_1_v$v.png $D 512x512 "$KEY" "$DAY $IC Subject: a soft loose bundle of violet thread/cotton fibre with light cream highlights, rounded soft folds (must not look like a brick). Palette: violet #7E57C2." &
  gen $T/anchors/mana_1_v$v.png $D 512x512 "$KEYMANA" "$DAY $IC Subject: a glowing pink-magenta teardrop mana crystal with small sparks, no gloss. Palette: magenta-pink #D94FA8." &
done
wait
echo DONE

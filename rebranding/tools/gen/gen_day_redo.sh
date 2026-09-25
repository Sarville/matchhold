#!/bin/bash
# T2 redo: cloth_3/4 (рулоны), wood_2/4/8 (v2/v3), реф = утверждённый якорь класса + ref-day-tiles
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
A=out/tiles/anchors
declare -A ANCH=([grain]=grain_1_v2 [wood]=wood_1_v2 [stone]=stone_1_v2 [clay]=clay_1_v2 [cloth]=cloth_1_v8)
declare -A PAL=([grain]="honey gold" [wood]="chestnut brown" [stone]="cool grey" [clay]="terracotta red" [cloth]="violet #7E57C2 with lavender-cream stripes")
# id|subject|палитра (перекрывает класс, необязательно)
ITEMS=(
"cloth_3|a single cylindrical ROLL of violet fabric lying on its side, tightly rolled like a carpet or a bolt of cloth, the round spiral end of the roll clearly visible, tied with one thin cream ribbon; NOT folded, NOT flat|"
"cloth_4|two royal violet fabric ROLLS lying side by side (cylindrical bolts of cloth, round spiral ends visible), with a woven gold pattern and gold trim at the ends; NOT folded, NOT flat|royal violet with gold"
"wood_2|ONE single smooth planed wooden plank lying diagonally, a long flat board, no straps, no stack|"
"wood_4|ONE single dark hardwood log lying diagonally with a visible round end and rings, darker than the level-1 logs, only one log|dark brown"
"wood_8|ONE single wooden plank whose long edges have a thin gold rim; it must look like a wooden board (visible wood grain on the face), not a box and not a gold bar|brown with gold"
)
for V in 2 3; do
for it in "${ITEMS[@]}"; do
  IFS='|' read -r id subj pal <<<"$it"; c=${id%_*}; lvl=${id#*_}
  k="$KEY"; [ "$c" = cloth ] && k="$KEYMANA"
  while (( $(jobs -r | wc -l) >= 6 )); do sleep 3; done
  gen out/tiles/icons-day/${id}_v$V.png "$A/${ANCH[$c]}.png $D" 512x512 "$k" "$DAY $IC Subject: $subj. This is level $lvl of the series '$c': the first attached image is the approved level-1 anchor of the same series: keep exactly its camera angle, outline weight, lighting and family of shapes, but this level is a clearly richer, more valuable upgrade. The second attached image is a style reference only. Palette: ${pal:-${PAL[$c]}}." &
done
done
wait
echo DONE

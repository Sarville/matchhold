#!/bin/bash
# ночные мечи и щиты ур. 2-3: явные отличия силуэта от ур. 1 и друг от друга (v2, v3)
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
kf() { echo "The whole background is a solid flat #$1 (no gradient, no shadow, no fringe); nothing else in the artwork is $2. One object only, centered, no ground shadow, no text."; }
KM="$(kf FF00FF pink-magenta)"; KG="$(kf 00FF00 green)"
NA=out/tiles/night-anchors
NIC='A single night game tile icon on a dark tile: an emblem, centered, fills about 66% of the canvas, no plate, no frame, no ground shadow, readable at 52 px, lighter and more luminous than a dark navy plate, soft glow in the given colour. The first attached image is the level-1 icon of the same series: keep its camera angle, outline weight, lighting and glow style, BUT this level must have a CLEARLY DIFFERENT, bigger and richer silhouette that is unmistakable from level 1 even at 52 px. The second attached image is the night style reference, style only.'
# id|ключ|refs|subject
ITEMS=(
"stone_2|M|$NA/stone_1_v2.png|Subject: a broad steel broadsword, noticeably longer and wider than the level-1 sword, with a wide straight steel crossguard, a deep central groove (fuller) along the blade and a round bronze pommel, same diagonal pose (tip up-right). Glow: steel blue."
"stone_3|G|$NA/stone_1_v2.png|Subject: a magnificent long silver sword, the biggest of the steel tier: polished bright blade, a large winged ornate steel crossguard with curved wing-like tips, a red ruby gem set in the hilt and pommel, same diagonal pose (tip up-right). No gold, silver only, plus the red gem. Glow: bright steel blue."
"wood_2|M|$NA/wood_1_v1.png|Subject: a round wooden shield reinforced with two thick dark iron straps forming a big cross over the planks, a ring of large iron rivets, front view; visibly sturdier than the level-1 shield and with the cross as its main feature. Glow: warm golden brown."
"wood_3|G|$NA/wood_1_v1.png|Subject: a larger round shield with a thick polished steel rim, a spiked steel boss in the centre, and a bold painted heraldic emblem (a red and cream sun or star) covering the planks; the emblem must be the main feature and clearly visible. Front view. Glow: warm golden brown."
)
for V in 2 3; do
for it in "${ITEMS[@]}"; do
  IFS='|' read -r id kk ref subj <<<"$it"
  k="$KM"; [ "$kk" = G ] && k="$KG"
  while (( $(jobs -r | wc -l) >= 6 )); do sleep 3; done
  gen out/tiles/icons-night/${id}_v$V.png "$ref $N" 512x512 "$k" "$NIGHT $NIC Subject: ${subj#Subject: }" &
done
done
wait
echo DONE

#!/bin/bash
# T3+T4: ночные серии (25) и грани дракона (3), 1 вариант. Реф: ночной якорь класса, дневная иконка того же уровня, ref-night-tiles
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
declare -A KEYS=([M]="$(kf FF00FF pink-magenta)" [G]="$(kf 00FF00 green)" [C]="$(kf 00FFFF cyan-turquoise)")
NA=out/tiles/night-anchors; ID=out/tiles/icons-day
declare -A NANCH=([grain]=grain_1_v1 [stone]=stone_1_v2 [wood]=wood_1_v1 [clay]=clay_1_v3 [cloth]=cloth_1_v1 [mana]=mana_1_v1)
declare -A DAYV=([cloth_3]=2 [cloth_4]=2 [wood_2]=2 [wood_4]=2 [wood_8]=2 [wood_9]=3)
NIC='A single night game tile icon on a dark tile: an emblem, centered, fills about 66% of the canvas, no plate, no frame, no ground shadow, readable at 52 px, lighter and more luminous than a dark navy plate, with a soft glow in the given colour. Attached images: the first is the approved level-1 NIGHT icon of the same series (keep exactly its camera angle, outline weight, lighting, glow style and family of shapes); the second is the DAY icon of the same class and level (use only colour family and richness hints); the third is the night style reference (palette, glow), style only, do not copy its icons.'
# id|ключ|subject+glow ; ключ: M пурпурный, G зелёный, C бирюзовый (не совпадает с цветом предмета или свечением)
ITEMS=(
"grain_2|M|hauntedArmour: an empty knight helmet on a stand with glowing green eyes. Glow: green."
"grain_3|M|earthElemental: a mossy stone golem head with a green glow. Glow: green."
"grain_4|M|demon: a horned demonic eye with red-orange flame. Glow: red-orange."
"clay_2|G|spider: a spider sitting on a cobweb. Glow: pale orange."
"clay_3|C|waterElemental: a water drop with a friendly-scary face. Glow: blue."
"clay_4|C|imp: a flask of green potion with a tiny imp inside. Glow: orange-red."
"cloth_2|C|lizardman: a swamp vine and a scaly lizard head. Glow: violet."
"cloth_3|G|fireElemental: a flame with a face. Glow: orange."
"cloth_4|G|warlock: a dark portal with golden horns and violet magic. Glow: violet."
"stone_2|M|a steel sword with a crossguard, same diagonal pose (tip up-right). Glow: steel blue."
"stone_3|M|a polished steel sword with an ornate hilt, same diagonal pose. Glow: steel blue."
"stone_4|G|a dark steel blade with a red flame along it, same diagonal pose. Glow: red-orange."
"stone_5|G|a dark blade with brighter fire, same diagonal pose. Glow: red-orange."
"stone_6|G|a dark blade wrapped in strong fire, same diagonal pose. Glow: red-orange."
"stone_7|M|an icy blue blade with a cold glow and a golden hilt, same diagonal pose. Glow: ice blue."
"stone_8|M|a brighter icy blade with a golden hilt, same diagonal pose. Glow: ice blue."
"stone_9|M|an icy blade with a golden hilt and a halo, same diagonal pose. Glow: ice blue."
"wood_2|M|a wooden round shield with rivets, front view. Glow: warm golden brown."
"wood_3|M|a round wooden shield with an iron rim and an emblem, front view. Glow: warm golden brown."
"wood_4|M|a dark iron kite shield, front view. Glow: warm golden brown."
"wood_5|M|a dark iron kite shield with a central spike, front view. Glow: warm golden brown."
"wood_6|M|a dark iron kite shield with a coat of arms, front view. Glow: warm golden brown."
"wood_7|M|a gilded shield with faint glowing runes, front view. Glow: gold."
"wood_8|M|a gilded shield with brighter runes, front view. Glow: gold."
"wood_9|M|a gilded shield with brightest runes and a halo, front view. Glow: gold."
)
for it in "${ITEMS[@]}"; do
  IFS='|' read -r id kk subj <<<"$it"; c=${id%_*}; l=${id#*_}
  dv=${DAYV[$id]:-1}
  while (( $(jobs -r | wc -l) >= 6 )); do sleep 3; done
  gen out/tiles/icons-night/${id}_v1.png "$NA/${NANCH[$c]}.png $ID/${id}_v$dv.png $N" 512x512 "${KEYS[$kk]}" "$NIGHT $NIC This is level $l of the series '$c', a clearly richer upgrade of level 1. Subject: $subj" &
done
# T4: грани дракона, драматичнее, glow сильнее
DR=(
"grain|M|a swirling gust of wind carrying a green leaf. Glow: strong green."
"clay|G|a sharp icy blue crystal with frost. Glow: strong cold blue."
"cloth|G|a bright roaring flame. Glow: strong orange-yellow."
)
for it in "${DR[@]}"; do
  IFS='|' read -r c kk subj <<<"$it"
  while (( $(jobs -r | wc -l) >= 6 )); do sleep 3; done
  gen out/tiles/icons-dragon/dragon_${c}_v1.png "$NA/${NANCH[$c]}.png $N" 512x512 "${KEYS[$kk]}" "$NIGHT A single dramatic night game tile icon (dragon-battle face), an emblem centered, fills about 66% of the canvas, no plate, no frame, no ground shadow, readable at 52 px, more luminous than a dark navy plate, glow stronger than on normal night icons. The first attached image is the night icon of the same class (keep its camera, outline weight and lighting); the second is the night style reference, style only. Subject: $subj" &
done
wait
echo DONE

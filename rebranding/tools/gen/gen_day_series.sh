#!/bin/bash
# T2: дневные серии (25 иконок, по 1 варианту), реф = утверждённый якорь класса + ref-day-tiles
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
"grain_2|a fuller, bound wheat sheaf with a bow and more grains, richer gold|"
"grain_3|a roasted chicken leg on the bone, golden-brown glaze|golden brown"
"grain_4|a glazed ham on the bone with herbs, the richest food|glazed golden brown"
"stone_2|a cut grey stone ingot|"
"stone_3|a stack of three grey stone ingots|"
"stone_4|an ember rock with glowing orange lava cracks|dark grey with orange"
"stone_5|a dark obsidian ingot with red veins|dark charcoal with red"
"stone_6|a stack of three dark obsidian ingots with red veins|dark charcoal with red"
"stone_7|a pale blue icy crystal shard|pale ice blue"
"stone_8|a blue steel ingot with a cold glow|steel blue"
"stone_9|a stack of three blue steel ingots with the brightest cold glow|steel blue, icy white"
"wood_2|a smooth planed wooden plank|"
"wood_3|a stack of three planks|"
"wood_4|a dark hardwood log|dark brown"
"wood_5|a dark hardwood plank|dark brown"
"wood_6|a stack of three dark hardwood planks|dark brown"
"wood_7|a magic wooden branch with shimmering green leaves|brown with emerald green"
"wood_8|a wooden plank with a gold rim|brown with gold"
"wood_9|a stack of three gilded planks with a soft warm glow|brown with gold"
"clay_2|one baked red brick|"
"clay_3|a neat stack of three red bricks with visible mortar edges|"
"clay_4|a piece of brick wall topped with a small tower crenellation|"
"cloth_2|a stack of two or three folded violet cloths, layered, with lavender-cream stripes|"
"cloth_3|a neat violet cloth roll (bolt of fabric) tied with a cream ribbon, round rolled end visible|"
"cloth_4|two royal violet cloth rolls with a woven pattern and gold trim|royal violet with gold"
)
for it in "${ITEMS[@]}"; do
  IFS='|' read -r id subj pal <<<"$it"; c=${id%_*}; lvl=${id#*_}
  k="$KEY"; [ "$c" = cloth ] && k="$KEYMANA"
  while (( $(jobs -r | wc -l) >= 6 )); do sleep 3; done
  gen out/tiles/icons-day/${id}_v1.png "$A/${ANCH[$c]}.png $D" 512x512 "$k" "$DAY $IC Subject: $subj. This is level $lvl of the series '$c': the first attached image is the approved level-1 anchor of the same series: keep exactly its camera angle, outline weight, lighting and family of shapes, but this level is a clearly richer, more valuable upgrade. The second attached image is a style reference only. Palette: ${pal:-${PAL[$c]}}." &
done
wait
echo DONE

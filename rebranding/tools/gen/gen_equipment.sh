#!/bin/bash
# Иконка «экипировка» v2: щит и меч (вместо молота и точила). Из rebranding/: bash tools/gen/gen_equipment.sh
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/3fd893fa-4392-496e-b52d-1567a942e2a4/scratchpad}
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left. A thin outline slightly darker than the object own hue, never black. Palette: warm sand beige, honey gold, chestnut brown, steel grey, cream white.'
KEY='The whole background is a solid flat #FF00FF (no gradient, no shadow, no fringe); nothing else in the artwork is pink or magenta. One object only, centered, no ground shadow, no text.'
NEG='Avoid: text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them where the prompt says, otherwise use them for style, palette and material only. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $4 $KEY $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
L=out/icons/loot
P="$DAY A single game item icon (armor and weapon set): a round wooden shield with a steel rim and a central iron boss in front, and a straight steel sword crossed diagonally behind it with the hilt and golden crossguard sticking out at the lower left and the blade tip at the upper right. Bold simple readable silhouette, bright clear colors with strong contrast so it reads at 40 pixels. Same style, outline weight and material feel as the attached bomb and potion icons. Fills about 75% of the canvas."
gen $L/loot_equipment_v2.png "$L/loot_bomb_v1.png $L/loot_health_potion_v1.png out/tiles/keyed-night/wood_1_v1.png out/tiles/keyed-night/stone_1_v2.png" 512x512 "$P" &
gen $L/loot_equipment_v3.png "$L/loot_bomb_v1.png $L/loot_health_potion_v1.png out/tiles/keyed-night/wood_1_v1.png out/tiles/keyed-night/stone_1_v2.png" 512x512 "$P Make the shield slightly larger than the sword; the sword is fully visible, not hidden." &
wait
echo DONE

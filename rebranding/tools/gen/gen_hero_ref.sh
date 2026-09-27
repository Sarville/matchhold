#!/bin/bash
# Реф-лист героя: 3 варианта. Запуск из rebranding/.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/f6ddb6fb-bf5a-42c9-8333-431a964eaff3/scratchpad}
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left. A thin outline slightly darker than the object own hue (about 2-3% of the object size), never black. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white, with a deep cobalt blue accent.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: use them for the character (blue hood), style, palette and material. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $4 Avoid: text, letters, numbers, labels, grid, logos, watermark, photorealism, glossy plastic, pixel art, thick black outlines, ground shadow, background scenery, pink or magenta inside the character. Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
BASE="[DAY] Character reference sheet on a flat solid #FF00FF background (no gradient, no shadow, no fringe): a small friendly young village builder-hero, chunky chibi proportions about 2.5 heads tall, big expressive dark eyes, chestnut-brown tunic, wide leather belt with a small hammer, a cobalt-blue hood and a blue scarf that trails behind him, cream sleeves, brown gloves, sturdy brown boots, a short steel sword with a gold guard in the right hand, no shield. Three poses side by side with clear gaps, all facing right, all the same scale and the same ground line: neutral standing, mid-stride walking, sword raised for a strike. Same outline weight and same colors in every pose, readable silhouette at a very small size."
gen out/anim/hero/hero_ref_v1.png "refs/ref-night-layout.png refs/ref-day-layout.png" 2304x768 "$BASE" &
gen out/anim/hero/hero_ref_v2.png "refs/ref-night-layout.png refs/ref-day-layout.png" 2304x768 "$BASE Make the head slightly larger (3 heads tall), the hood pointed with a small tassel, and the tunic a warmer orange-brown." &
gen out/anim/hero/hero_ref_v3.png "refs/ref-night-layout.png refs/ref-day-layout.png" 2304x768 "$BASE Give him a short cape instead of the trailing scarf, a leather shoulder strap and a slightly heroic stance." &
wait
echo DONE

#!/bin/bash
# Реф-листы монстров (A2, метод-проверка): zombie, skeleton. 3 варианта каждый. Запуск из rebranding/.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/d6945f1c-fd00-403e-a79e-f106200f409c/scratchpad}
mkdir -p "$S"
NIGHT='[NIGHT] Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (chunky rounded forms, soft ambient occlusion, NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light and a gentle glow on key details. Thin outline slightly darker than the object own hue, never black. Clean, readable silhouette against dark backgrounds.'
gen() { # out refs size key prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached reference is for overall style/lighting/matte look only, not for the character design. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $NIGHT $5 Three poses side by side with clear gaps, all facing right, all the same scale and the same ground line: neutral standing, mid-move, and an attack pose. Chunky rounded shapes, same outline weight in every pose, readable silhouette. Cute-menacing, no gore, no blood. Avoid: text, letters, numbers, labels, grid, logos, watermark, photorealism, glossy plastic, pixel art, thick black outlines, ground shadow, background scenery, $4 inside the character. Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
N=refs/ref-night-layout.png
Z="Monster character reference sheet on a flat solid #FF00FF background (no gradient, no shadow, no fringe): a ragged green-skinned zombie, torn brown clothes, arms forward, shuffling gait, dim green glow in the eyes."
gen out/anim/monsters/zombie/zombie_ref_v1.png "$N" 2304x768 "pink or magenta" "$Z"
gen out/anim/monsters/zombie/zombie_ref_v2.png "$N" 2304x768 "pink or magenta" "$Z Make it a bit shorter and rounder, more chibi, patched grey-green shirt." &
gen out/anim/monsters/zombie/zombie_ref_v3.png "$N" 2304x768 "pink or magenta" "$Z Give it one stiff raised arm and a lopsided head tilt for a more comedic silhouette." &
K="Monster character reference sheet on a flat solid #FF00FF background (no gradient, no shadow, no fringe): a skeleton archer with a cracked skull, tattered dark cloak, a wooden bow in hand, dim violet glow in the eye sockets."
gen out/anim/monsters/skeleton/skeleton_ref_v1.png "$N" 2304x768 "pink or magenta" "$K" &
gen out/anim/monsters/skeleton/skeleton_ref_v2.png "$N" 2304x768 "pink or magenta" "$K Make it a bit shorter and chunkier, more chibi, quiver of arrows on the back." &
gen out/anim/monsters/skeleton/skeleton_ref_v3.png "$N" 2304x768 "pink or magenta" "$K Hooded cloak with a pointed cowl, bow held two-handed and half-drawn." &
wait
echo DONE

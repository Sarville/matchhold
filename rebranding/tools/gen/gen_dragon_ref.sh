#!/bin/bash
# Реф-лист дракона (боссфайт), 3 варианта, вид сбоку. Запуск из rebranding/.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/c7bcb9cf-bb55-40aa-bdc2-2c5d1b6637da/scratchpad}
mkdir -p "$S"
NIGHT='[NIGHT] Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (chunky rounded forms, soft ambient occlusion, NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light and a gentle glow on key details. Thin outline slightly darker than the object own hue, never black. Clean, readable silhouette against dark backgrounds.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached reference is for overall style/lighting/matte look only, not for the character design. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $4 Avoid: text, letters, numbers, labels, grid, logos, watermark, photorealism, glossy plastic, pixel art, thick black outlines, ground shadow, background scenery, pink or magenta inside the character. Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
N=refs/ref-night-layout.png
D="Dragon boss character reference sheet on a flat solid #FF00FF background (no gradient, no shadow, no fringe): a chunky cute-menacing dragon, side view facing right, dark charcoal-and-crimson scales, a row of blunt dorsal spines along the neck and back, membranous wings with a warm orange glow along the veins, short thick legs, a long tapering tail, warm ember glow from inside the half-open mouth. Chibi-adjacent proportions (big head, short snout, stocky body), NOT realistic/scary — cute-menacing like the other monsters, no gore, no blood. Three poses side by side with clear gaps, all facing right, all the same scale and the same ground line: (1) sitting/crouched idle with wings folded, (2) flying with wings spread mid-flap, (3) wings spread wide rearing up for a wing-buffet attack. Same outline weight and same colors in every pose, readable silhouette at a very small size."
gen out/anim/dragon/dragon_ref_v1.png "$N" 2304x768 "$NIGHT $D" &
gen out/anim/dragon/dragon_ref_v2.png "$N" 2304x768 "$NIGHT $D Make it stockier and rounder, shorter snout, bigger head, more chibi." &
gen out/anim/dragon/dragon_ref_v3.png "$N" 2304x768 "$NIGHT $D Give it two small curved horns and a brighter, more saturated orange glow along the spines and wing veins." &
wait
echo DONE

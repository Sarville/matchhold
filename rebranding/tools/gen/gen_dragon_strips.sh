#!/bin/bash
# Тело (5 полос 2x2), голова (3 позы), сегмент шеи — по одобренному dragon_ref_v3. Запуск из rebranding/.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/c7bcb9cf-bb55-40aa-bdc2-2c5d1b6637da/scratchpad}
mkdir -p "$S" out/anim/dragon
R=out/anim/dragon/dragon_ref_v3.png
NIGHT='[NIGHT] Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (chunky rounded forms, soft ambient occlusion, NO glossy plastic highlights). Deep indigo shadows, cool moonlight, warm ember-orange glow accents. Thin outline slightly darker than the object own hue, never black.'
gen() { # out size prompt refs=$R
  [ -f "$1" ] && return
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image, target size $2 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $3 Avoid: text, letters, numbers, labels, grid lines, borders, logos, watermark, photorealism, glossy plastic, pixel art, thick black outlines, ground shadow, scenery, extra characters. Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i "$R" \
  > "$S/$(basename $1).log" 2>&1
}

BODY="[NIGHT] Animation frames of the ONE dragon boss from the attached reference sheet, on a flat solid #FF00FF background (no gradient, no shadow, no fringe): a 2 x 2 arrangement of four equal square cells (top-left, top-right, bottom-left, bottom-right; the cells are invisible, NOT drawn), frame order: top-left, top-right, bottom-left, bottom-right. In every cell the SAME dragon, facing right, same design, colors, proportions, outline weight and same scale as in the reference; centered in the cell so the whole pose (including spread wings/tail) fits inside with a small margin; it never touches or crosses its cell edge. Cute-menacing, no gore, no blood. Action:"
gen out/anim/dragon/dragon_idle_v1.png 1536x1536 "$BODY sitting/crouched idle: frame 1 wings folded settled, frame 2 chest expands (breathing in), frame 3 chest relaxes (breathing out), frame 4 tail flicks slightly to the side. Feet/haunches stay on the same ground line at 85% of the cell height in every frame." &
gen out/anim/dragon/dragon_fly_v1.png 1536x1536 "$BODY flying in place, a 4-frame wingbeat cycle: frame 1 wings fully up, frame 2 wings mid-downstroke, frame 3 wings fully down, frame 4 wings mid-upstroke. Body stays centered at the same height in all four frames (looping cycle)." &
gen out/anim/dragon/dragon_landing_v1.png 1536x1536 "$BODY landing sequence, frame 1 still airborne with wings braking (spread wide, body tilted back), frame 2 legs reaching for the ground, frame 3 wings folding in as feet touch down, frame 4 fully settled crouched on the ground with wings folded (matches the idle pose)." &
gen out/anim/dragon/dragon_windup_v1.png 1536x1536 "$BODY winding up for a wing-buffet attack: frame 1 wings start spreading wide, frame 2 wings spread further and body leans back, frame 3 wings pulled back fully spread at maximum stretch (about to slam forward), frame 4 same fully wound-up pose held (anticipation hold)." &
gen out/anim/dragon/dragon_buffet_v1.png 1536x1536 "$BODY striking with a wing-buffet attack: frame 1 wings snapping forward from the wound-up pose, frame 2 wings fully slammed forward at full extension (the strike impact), frame 3 wings starting to recoil back, frame 4 wings settling back toward the folded idle pose." &

HEAD="[NIGHT] The head of the ONE dragon boss from the attached reference sheet, on a flat solid #FF00FF background (no gradient, no shadow, no fringe): three poses side by side with clear gaps, all the same head, same angle (side view facing right), same scale, same colors and outline weight, only the mouth changes: (1) mouth fully closed, (2) mouth half open with a faint ember glow inside, (3) mouth wide open roaring with a bright ember glow and visible teeth. Each head centered in its own slot, cropped tight to the head/jaw/horns only (no neck, no body)."
gen out/anim/dragon/dragon_head_v1.png 768x288 "$HEAD" &

NECK="[NIGHT] ONE single dragon neck scale segment, on a flat solid #FF00FF background (no gradient, no shadow, no fringe): a short chunky ring-shaped segment of the dragon neck from the attached reference (same scales, same dark charcoal-and-crimson coloring, same small dorsal spine on top), designed to repeat/stack end to end into a bendable neck chain. Side view, facing right, filling most of the square frame, no other body parts."
gen out/anim/dragon/dragon_neck_v1.png 256x256 "$NECK" &

wait
echo DONE

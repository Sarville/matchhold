#!/bin/bash
cd /home/user/projects/matchhold/rebranding || exit 1
S=/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light and a gentle glow on key details.'
NEG='Avoid: text, letters, numbers, logos, watermark, signature, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage, characters, birds, frame, pink or magenta colors inside the artwork.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=medium --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them where the prompt says so, otherwise use them for mood, palette and material only. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $4 $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
E=out/env
SCENE="the same scene as the attached full background (windmill on the left hill, cottages left and right, dirt road, rolling hills, forest, distant mountains, small lake)"
FGDP="[DAY] Out-of-focus FOREGROUND layer for a tall phone screen (vertical 1:2) with a genuinely TRANSPARENT background (real alpha channel, no colored background, no magenta). VERY SMALL and sparse: only two small blurry tufts of sage-green leaves, grass blades, one or two small white flowers and a small mossy stone, tucked into the bottom-left and bottom-right corners; each tuft is only about 18% of the width and 7% of the height and sits right at the bottom edge. NOTHING at the top of the canvas, nothing on the left and right edges above the tufts, nothing in the middle. Every leaf ends with its own soft organic tip, no straight cut edges. Everything else is fully transparent. Strong depth-of-field blur (bokeh), soft edges."
gen $E/fg/fg_day_port_v3.png "$E/fg/fg_day_land_v2.png $E/fg/fg_day_port_v2.png" 1440x2880 "$DAY $FGDP" &
FGNP="[NIGHT] Out-of-focus FOREGROUND layer for a tall phone screen (vertical 1:2) with a genuinely TRANSPARENT background (real alpha channel, no colored background, no magenta). VERY SMALL and sparse: only two small blurry tufts at the bottom-left and bottom-right corners, each with dark ferns, a small piece of mossy stone ruin and one small iron lantern or torch with a soft warm orange glow; each tuft is only about 18% of the width and 7% of the height and sits right at the bottom edge. NOTHING at the top of the canvas, nothing on the left and right edges above the tufts, nothing in the middle. Everything trails off with its own soft outline, no straight cut edges. Everything else is fully transparent. Strong depth-of-field blur (bokeh), soft edges."
gen $E/fg/fg_night_port_v2.png "$E/fg/fg_night_land_v2.png $E/fg/fg_night_port_v1.png" 1440x2880 "$NIGHT $FGNP" &
wait
echo DONE

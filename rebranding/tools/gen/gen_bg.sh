#!/bin/bash
cd /home/user/projects/matchhold/rebranding || exit 1
S=/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light and a gentle glow on key details.'
NEG='Avoid: text, letters, numbers, logos, watermark, signature, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, cropped edges, sharp foreground details, multiple views, collage, characters, birds, frame.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=medium --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them where the prompt says so, otherwise use them for mood, palette and material only, do not copy their composition. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG, opaque. $4 $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
SCENE1="Stage 1, Village: green meadows and rolling hills, a few small cottages with thatched and red roofs, a wooden windmill, a dirt road, a forest, distant mountains"
DAYLAND="Wide 16:9 background illustration for a fantasy village game, soft depth-of-field: distant mountains and sky are very soft, the mid-ground is gently blurred, nothing is sharp. $SCENE1. Composition: the central 40% of the width is calm and low-contrast (only soft sky, haze and distant hills, no bright spots) so a game board can sit on top; all landmarks (cottages, windmill, road, forest) are placed in the left and right thirds. Light sky at the top, warmer toward the horizon. No characters, no birds, no text, no frame."
for v in 1 2; do gen out/env/bg/bg_s1_day_land_v$v.png refs/ref-day-layout.png 3840x2160 "$DAY $DAYLAND" & done
wait
echo STAGE1 DONE

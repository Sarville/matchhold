#!/bin/bash
cd /home/user/projects/matchhold/rebranding || exit 1
S=/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left. A thin outline slightly darker than the object own hue, never black. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light. Thin outline slightly darker than the object own hue, never black.'
KEY='The whole background is a solid flat #FF00FF (no gradient, no shadow, no fringe); nothing else in the artwork is pink or magenta. One object only, centered, no ground shadow, no text.'
NEG='Avoid: text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=medium --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them where the prompt says, otherwise use them for style, palette and material only. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $4 $KEY $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
F=out/env/floor
SKD="$DAY One square recessed socket seen straight from the front, rounded corners (radius about 12% of the side). A THIN, NEAT rim: the raised border is very slim and clean, only about 4% of the side wide, with a crisp narrow bevel, the same warm sand color and texture as the first attached socket (its rim is too thick, make it much thinner and more precise). The recessed inner area is LARGE, about 92% of the socket width, flat pale sand-beige with a soft inner shadow on the top and left inner edges. Clean, precise, perfectly symmetric edges, no chips, no cracks, no wobbling outline. The socket occupies the central 96% of the canvas. Matte, no gloss, no icon inside."
for v in 1 2; do gen $F/socket_day_v3_$v.png "$F/socket_day_v2.png refs/ref-day-tiles.png" 1024x1024 "$SKD" & done
wait
echo DONE

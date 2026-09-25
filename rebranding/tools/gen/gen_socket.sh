#!/bin/bash
# Генерация дневных артов поля через codex gpt-5.6-terra, reasoning medium
cd /home/user/projects/matchhold/rebranding || exit 1
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine, NO glassy sparkle. Warm afternoon light from the top-left, soft warm shadow toward the bottom-right. A thin outline slightly darker than the object own hue (about 2-3% of the object size), never black. Clean, readable silhouette. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NEG='Avoid: text, letters, numbers, logos, watermark, signature, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, cropped edges, blurry subject, multiple views, collage.'

gen() { # id out ref size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=medium --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached image is a style/mood reference only (palette, material, light); do not copy its composition. Target size $4 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $5 $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$2 . Do not overwrite existing files. Print the saved path and dimensions." -i "$3" \
  > "/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad/$(basename $2).log" 2>&1
}
SOCKET="One square recessed socket seen from the front, rounded corners (radius about 14% of the side), a soft inner shadow on the top and left inner edges and a faint light lip on the bottom and right, in slightly darker warm sand than the floor. Occupies the central 88% of the canvas. Matte, no gloss, no icon inside. Background outside the socket: solid flat #FF00FF only, no white, no gradient, no drop shadow, no fringe. No dark outer rim."
gen x out/env/floor/socket_day_v2.png refs/ref-day-tiles.png 1024x1024 "$DAY $SOCKET"
echo DONE

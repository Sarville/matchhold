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

FRAME="A square wooden game-board frame, seen straight from the front, flat orthographic view, perfectly symmetrical. Thick warm chestnut-brown planks with soft vertical wood grain, a lighter bevel on the inner edge, small dark-brass corner brackets and rivets. The frame is a hollow square ring: uniform thickness on all four sides, outer edge inset 32 px from the canvas edge, thickness 144 px on every side. The inside opening is a perfect square. The top beam is completely bare and flat. A few sage green ivy vines climb only the left side and the two bottom corners, slightly overlapping the frame, never entering the opening or the top beam. Fill the opening and everything outside the frame with solid flat #FF00FF (no gradient, no shadow, no fringe). Matte, no gloss. No tiles, no buildings, no people, no text."
FLOOR="A flat top-down texture, seamless-feeling, warm sand-beige packed earth and sandstone with very subtle mottling and faint fine cracks, slightly darker vignette toward the four corners. Matte. No grid lines, no objects, no text."
SOCKET="One square recessed socket seen from the front, rounded corners (radius about 14% of the side), a soft inner shadow on the top and left inner edges and a faint light lip on the bottom and right, in slightly darker warm sand than the floor. Occupies the central 88% of the canvas. Matte, no gloss, no icon inside. Fully transparent background if possible, otherwise solid flat #FF00FF."

for v in 1 2 3; do gen x out/env/frame/frame_day_v$v.png refs/ref-day-layout.png 2048x2048 "$DAY $FRAME" & done
for v in 1 2; do gen x out/env/floor/floor_day_v$v.png refs/ref-day-tiles.png 2048x2048 "$DAY $FLOOR" & done
gen x out/env/floor/socket_day_v1.png refs/ref-day-tiles.png 512x512 "$DAY $SOCKET" &
wait
echo ALL DONE

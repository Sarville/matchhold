#!/bin/bash
cd /home/user/projects/matchhold/rebranding || exit 1
S=/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (chunky rounded forms, soft ambient occlusion, NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light and a gentle glow on key details. Thin outline slightly darker than the object own hue, never black. Clean, readable silhouette against dark backgrounds.'
NEG='Avoid: text, letters, numbers, logos, watermark, signature, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, cropped edges, blurry subject, multiple views, collage.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them exactly where the prompt says so, otherwise use them for palette, material and light only. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $4 $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
FRAME="The exact same square game-board frame as the first attached image (the day frame): identical outline, identical thickness on all four sides, identical square inner opening, identical ivy placement, identical corner brackets, but built from cool blue-grey cut stone blocks with mortar lines and worn edges, ivy darker and slightly bluish, faint moonlit rim light on the top-left edges, small dark-iron corner brackets. Keep the top beam bare and flat. Fill the opening and everything outside the frame with solid flat #FF00FF (no gradient, no shadow, no fringe). Matte, no gloss. No tiles, no buildings, no people, no text."
FLOOR="A flat top-down texture, deep navy-blue slate with very subtle mottling and faint fine cracks, same crack pattern density and scale as the first attached image (the day floor), slightly darker vignette toward the four corners, hint of cool moonlit sheen. Matte. No grid lines, no objects, no text."
SOCKET="One square recessed socket seen from the front, same shape, proportions and rounded corners as the first attached image (the day socket), a soft inner shadow on the top and left inner edges and a faint light lip on the bottom and right, in deep navy-blue slightly darker than the night floor. Occupies the central 88% of the canvas. Matte, no gloss, no icon inside. Background outside the socket: solid flat #FF00FF only, no white, no gradient, no drop shadow, no fringe. No dark outer rim."
for v in 1 2 3; do gen out/env/frame/frame_night_v$v.png "$S/frame_day_fit_key.png refs/ref-night-layout.png" 2048x2048 "$NIGHT $FRAME" & done
for v in 1 2; do gen out/env/floor/floor_night_v$v.png "out/env/floor/floor_day_v2.png refs/ref-night-tiles.png" 2048x2048 "$NIGHT $FLOOR" & done
gen out/env/floor/socket_night_v1.png "out/env/floor/socket_day_v2.png refs/ref-night-tiles.png" 1024x1024 "$NIGHT $SOCKET" &
wait; echo DONE

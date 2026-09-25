#!/bin/bash
cd /home/user/projects/matchhold/rebranding || exit 1
S=/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left, soft warm shadow toward the bottom-right. A thin outline slightly darker than the object own hue, never black. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NEG='Avoid: text, letters, numbers, logos, watermark, signature, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, blurry subject, multiple views, collage.'
FRAME="The first attached image is a strict GEOMETRY GUIDE (a flat brown ring on solid magenta, with darker squares in the four corners). Repaint it as a finished wooden game-board frame, keeping the ring geometry EXACTLY: the same outer edge, the same uniform thickness on all four sides (thin, about 7% of the canvas), the same perfect square opening, the same four corner squares (they become small dark-brass corner brackets with rivets). Do not make the frame thicker or the opening smaller. Warm chestnut-brown planks with soft wood grain and a subtle lighter bevel on the inner edge. The top beam is completely bare and flat. A few sage green ivy vines climb only the left side and the two bottom corners, slightly overlapping the frame, never entering the opening or the top beam. Keep the opening and everything outside the frame solid flat #FF00FF (no gradient, no shadow, no fringe). Straight front view, orthographic, symmetrical. Matte. No tiles, no buildings, no people, no text."
gen() {
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=medium --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image at 2048x2048 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. The second attached image is a style reference only (palette, material). $DAY $FRAME $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i "$S/frame_guide_thin.png" refs/ref-day-layout.png \
  > "$S/$(basename $1).log" 2>&1
}
for v in 1 2 3; do gen out/env/frame/frame_day_thin_v$v.png & done
wait; echo DONE

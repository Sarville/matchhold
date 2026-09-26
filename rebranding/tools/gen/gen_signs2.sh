#!/bin/bash
# Этап 2: ночной столбик по выбранному дневному (sign_level_day_v2) + ночной мини-фон по дневному ground_strip_v2.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/8cf97f12-1c34-4a07-9e32-fb51c227da2b/scratchpad}
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (chunky rounded forms, NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light. Thin outline slightly darker than the object own hue, never black.'
gen() { # out refs size key prompt
  [ -f "$1" ] && return
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The first attached image is the DAY version to be converted; the others are night style references. Target size $3 (if the native size differs, resize the whole picture to FIT INSIDE with ImageMagick and pad with the key colour; NEVER crop, NEVER stretch; at least 4% empty key-colour margin). PNG. $5 The whole background is a solid flat $4 (no gradient, no shadow, no fringe); nothing in the artwork is that colour. Avoid: people, text, letters, digits, symbols, logos, watermark, UI, photorealism, gloss, lens flare, pixel art, thick black outlines, buildings, trees, extra objects. Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
for v in 1 2; do
gen out/env/signs/sign_level_night_v$v.png "out/env/signs/keyed/sign_level_day_v2.png out/icons/hud/panel_plate_night_v1.png refs/ref-night-layout.png" 768x1024 '#FF00FF' "$NIGHT The EXACT same signpost as the first attached image (identical shape, proportions, post, crossarm, chains, board, plaque position and size, base with stones), converted to night: the chestnut wood becomes deep blue-brown, the brass becomes dark old bronze with faint warm highlights, the cream plaque becomes a dark navy-slate plaque (#2E3853) with a thin bronze rim, still completely empty; the stones and grass at the base are cool and dark. ADD one small warm-orange lantern hanging from the left end of the crossarm with a soft warm glow that lights the nearby wood. Nothing else changes." &
gen out/env/ground/ground_strip_night_v$v.png "out/env/ground/keyed/ground_strip_v2.png refs/ref-night-layout.png" 1536x256 '#FF00FF' "$NIGHT The same long horizontal strip of village ground as the first attached image (same layout: footpath in the middle, grass verges, tufts along the back edge, clean turf-and-soil lip at the front, same proportions and detail), converted to night: cool blue-teal grass, dark slate-blue soil and path with cool moonlit highlights, tiny pale flowers. Fills the canvas width edge to edge, ends continue seamlessly." &
done
wait; echo DONE

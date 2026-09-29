#!/bin/bash
# Снаряды и эффекты боя (сессия 10): стрела, огненный/тёмный снаряд, вспышка, шары луча, огонь на земле, ледяной блок.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/fxlogs}; mkdir -p "$S" out/fx
STYLE='Cozy fantasy village match-3 game art, warm soft matte hand-painted 3D look with chunky rounded forms, thin outline slightly darker than the object own hue (never black), NO glossy plastic highlights. The picture will be shown very small (about 20-40 px) in the game, so use ONE simple bold readable silhouette with high contrast and few details.'
NEG='Avoid: text, letters, logos, watermark, photorealism, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage, ground shadow.'
key() { echo "The whole background is a solid flat $1 (no gradient, no shadow, no fringe); nothing else in the artwork is that color."; }
gen() { # out key prompt
  [ -f "$1" ] && return
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are style references only (palette and material). Target size 1024x1024 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $STYLE $3 $(key $2) $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i refs/ref-day-layout.png out/ui/star/star_v1.png \
  > "$S/$(basename $1).log" 2>&1
}
gen out/fx/arrow_v1.png '#FF00FF' 'A single wooden arrow flying to the RIGHT, perfectly horizontal, seen from the side: steel arrowhead on the right tip, light wood shaft, cream-white feather fletching on the left end. The arrow spans about 90% of the canvas width and is centered vertically; it is slim, fill height only about 15% of the canvas.' &
gen out/fx/firebolt_v1.png '#00FF00' 'A single fire bolt flying to the RIGHT, perfectly horizontal: a bright round fireball head on the right (white-yellow core, orange edge) with a tapering tail of flames and a few sparks streaming to the LEFT. Spans about 90% of the canvas width, centered vertically, height about 35% of the canvas.' &
gen out/fx/arcane_v1.png '#00FF00' 'A single dark-magic bolt flying to the RIGHT, perfectly horizontal: a glowing violet orb head on the right (pale lilac core, deep purple edge) with a tapering wispy purple tail and a few tiny star sparks streaming to the LEFT. Spans about 90% of the canvas width, centered vertically, height about 35% of the canvas.' &
gen out/fx/burst_v1.png '#00FF00' 'A round fire explosion burst seen from the front: a roughly circular puff with white-yellow core, orange middle and red-brown wispy edge, a few flame tongues and sparks, symmetric, no smoke trail. Fills about 90% of the canvas, centered.' &
wait
gen out/fx/orb_ice_v1.png '#FF00FF' 'A round ball of ice magic seen from the front: pale white-blue glowing core, cyan-blue edge with a few small frost crystal spikes around it, symmetric. Fills about 85% of the canvas, centered.' &
gen out/fx/orb_fire_v1.png '#00FF00' 'A round ball of dragon fire seen from the front: white-yellow glowing core, orange-red flames swirling around it, a few flame tongues, symmetric. Fills about 85% of the canvas, centered.' &
gen out/fx/flames_v1.png '#00FF00' 'A grid of exactly 4 cells (2 columns x 2 rows, each cell 512x512, no borders or lines between them). Each cell contains ONE small ground fire: a single upright flame cluster about 60% of the cell width and 85% of the cell height, its base touching the bottom of the cell at the center, orange-red with a yellow core; the four flames differ slightly in shape as frames of a flickering animation (tongues leaning left, up, right, up). Same size and base position in all four cells.' &
gen out/fx/iceblock_v1.png '#FF00FF' 'A single upright block of translucent pale-blue ice, rounded chunky slab taller than wide (about 2:3), frosty white highlights on the edges, small icicles on top, see-through paler center. Fills about 85% of the canvas height, centered.' &
wait
echo DONE

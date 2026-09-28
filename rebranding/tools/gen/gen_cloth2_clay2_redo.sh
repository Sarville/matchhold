#!/bin/bash
# Редо cloth_2 (ящер зелёный -> песочный, конфликтовал по цвету с зелёными grain-иконками) и clay_2 (паутина ближе к красному)
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/d6945f1c-fd00-403e-a79e-f106200f409c/scratchpad}
mkdir -p "$S"
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light. Thin outline slightly darker than the object own hue, never black.'
NEG='Avoid: text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage.'
kf() { echo "The whole background is a solid flat #$1 (no gradient, no shadow, no fringe); nothing else in the artwork is $2. One object only, centered, no ground shadow, no text."; }
KEY_C="$(kf 00FFFF cyan-turquoise)"
KEY_G="$(kf 00FF00 green)"
gen() { # out refs key prompt
  [ -f "$1" ] && return
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them for composition and camera angle, but recolor as the prompt says. Target size 512x512 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $NIGHT $4 $3 $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
N=refs/ref-night-tiles.png
gen out/tiles/icons-night/cloth_2_v2.png "out/tiles/icons-night/cloth_2_v1.png $N" "$KEY_C" \
"A single night game tile icon (lizardman emblem): the same swamp vine wreath and coiled scaly lizard head as the attached reference, same pose, same camera angle, same outline weight, but recolor the lizard scales from green to a warm sand/tan colour (like pale desert khaki) with cream-beige belly and a darker sand-brown vine, keeping the cream-and-violet striped scarf. It must no longer read as green. Glow: soft violet. Fills about 66% of the canvas, no plate, no frame, no ground shadow, readable at 52 px."
gen out/tiles/icons-night/clay_2_v2.png "out/tiles/icons-night/clay_2_v1.png $N" "$KEY_G" \
"A single night game tile icon (spider emblem): the same spider sitting on a round cobweb as the attached reference, same pose, same camera angle, same outline weight, but recolor the web strands and spider body from orange-terracotta to a deeper red / rust-red, with brighter red-orange glowing eyes. Glow: warm red. Fills about 66% of the canvas, no plate, no frame, no ground shadow, readable at 52 px."
wait
echo DONE

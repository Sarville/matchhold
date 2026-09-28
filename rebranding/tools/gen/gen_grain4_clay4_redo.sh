#!/bin/bash
# Редо grain_4 (демон: красно-оранжевый огонь -> зелёный, как весь grain-чейн) и clay_4 (зелье имп: форма + зелёный -> синий)
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/d6945f1c-fd00-403e-a79e-f106200f409c/scratchpad}
mkdir -p "$S"
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light. Thin outline slightly darker than the object own hue, never black.'
NEG='Avoid: text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage.'
kf() { echo "The whole background is a solid flat #$1 (no gradient, no shadow, no fringe); nothing else in the artwork is $2. One object only, centered, no ground shadow, no text."; }
KEY_M="$(kf FF00FF pink-magenta)"
KEY_C="$(kf 00FFFF cyan-turquoise)"
gen() { # out refs key prompt
  [ -f "$1" ] && return
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them for composition and camera angle, but recolor/reshape as the prompt says. Target size 512x512 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $NIGHT $4 $3 $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
N=refs/ref-night-tiles.png
gen out/tiles/icons-night/grain_4_v2.png "out/tiles/icons-night/grain_4_v1.png $N" "$KEY_M" \
"A single night game tile icon (demon emblem): the same horned demonic stone eye as the attached reference, same pose, same camera angle, same outline weight, but recolor the flame around it from red-orange to a vivid green fire (matching the green glow of the other icons in this monster family), keep the eye itself glowing green instead of orange-red. Glow: strong green. Fills about 66% of the canvas, no plate, no frame, no ground shadow, readable at 52 px."
gen out/tiles/icons-night/clay_4_v2.png "out/tiles/icons-night/clay_4_v1.png $N" "$KEY_C" \
"A single night game tile icon (imp-in-a-bottle emblem): a small mischievous imp trapped inside a glass container, terracotta-brown rocky rim like the attached reference, but give the bottle a different, more angular hexagonal alchemical-vial silhouette (tall faceted vial with a narrow neck, not the round onion shape of the reference), and change the liquid inside from green to a glowing blue potion, imp silhouette still visible inside with small glowing orange eyes. Glow: blue. Fills about 66% of the canvas, no plate, no frame, no ground shadow, readable at 52 px."
wait
echo DONE

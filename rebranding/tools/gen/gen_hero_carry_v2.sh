#!/bin/bash
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/f6ddb6fb-bf5a-42c9-8333-431a964eaff3/scratchpad}
A=out/anim/hero
gen() {
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image, square, target 1536x1536 (resize with ImageMagick only if needed, never crop or stretch). PNG. $1 Avoid: text, letters, numbers, labels, grid lines, borders, logos, watermark, photorealism, glossy plastic, pixel art, thick black outlines, ground shadow, scenery, pink or magenta inside the character, extra characters. Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$A/hero_carry_walk_v2.png . Do not overwrite existing files. Print the saved path and dimensions." -i "$2" \
  > "$S/hero_carry_walk_v2.log" 2>&1
}
PROMPT="[DAY] Animation frames of ONE character on a flat solid #FF00FF background (no gradient, no shadow, no fringe): a 2 x 2 arrangement of four equal square cells (top-left, top-right, bottom-left, bottom-right; the cells are invisible, NOT drawn), frame order: top-left, top-right, bottom-left, bottom-right. In every cell the attached reference character (the small blue-hooded builder-hero, facing right), same costume, colors, proportions, outline weight and exactly the same scale as in the reference. He is WALKING RIGHT while carrying a heavy invisible box in both arms in front of his chest (arms bent forward, hands together as if cupping an invisible box at chest height, do NOT draw the box or any object). This is a walk cycle: the LEGS MUST clearly stride like the attached walking-reference (second image) — this is the most important part, the legs move a lot between frames, do not keep them in the same standing pose. Four distinct leg poses, same order and spacing as the walking reference: 0 right leg forward heel down / left leg back (contact pose), 1 legs passing close together body a little higher, 2 left leg forward / right leg back (contact pose), 3 legs passing close together again but mirrored from frame 1. Feet stay on the same ground line at 88% of the cell height in all four cells; the figure never touches or crosses its cell edge. Matte hand-painted 3D look."
gen "$PROMPT" "$A/hero_ref.png $A/hero_walk_v1.png"
echo DONE

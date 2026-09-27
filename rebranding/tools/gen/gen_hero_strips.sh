#!/bin/bash
# Полосы кадров героя: сетка 2x2 (кадры 0,1 сверху, 2,3 снизу). Запуск: [V=1] bash tools/gen/gen_hero_strips.sh [id ...]
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/f6ddb6fb-bf5a-42c9-8333-431a964eaff3/scratchpad}
V=${V:-1}
R=out/anim/hero/hero_ref.png; A=out/anim/hero
gen() { # id refs prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image, square, target 1536x1536 (resize with ImageMagick only if needed, never crop or stretch). PNG. $3 Avoid: text, letters, numbers, labels, grid lines, borders, logos, watermark, photorealism, glossy plastic, pixel art, thick black outlines, ground shadow, scenery, pink or magenta inside the character, extra characters. Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$A/hero_$1_v$V.png . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/hero_$1_v$V.log" 2>&1
}
HEAD="[DAY] Animation frames of ONE character on a flat solid #FF00FF background (no gradient, no shadow, no fringe): a 2 x 2 arrangement of four equal square cells (top-left, top-right, bottom-left, bottom-right; the cells are invisible, NOT drawn), frame order: top-left, top-right, bottom-left, bottom-right. In every cell the attached reference character (the small blue-hooded builder-hero, facing right), same costume, colors, proportions, outline weight and exactly the same scale as in the reference sheet; he stands centered in the cell with his feet on the same ground line at 88% of the cell height in all four cells; the figure never touches or crosses its cell edge. Each frame is a clearly different key pose. Matte hand-painted 3D look. In this strip his hands are EMPTY and the sword is not visible (only the small hammer stays on his belt), unless stated otherwise. Action:"
declare -A ACT=(
 [idle]="standing idle, a loop: 0 neutral stand, 1 chest slightly up and the blue scarf lifts, 2 weight shifted onto one leg with a small head tilt, 3 back to a slightly lower breathing pose."
 [walk]="walking right, a loop of four key poses: 0 contact pose right leg forward, 1 passing pose body a little higher legs together, 2 contact pose left leg forward, 3 passing pose. Arms swing opposite to the legs, the scarf streams behind."
 [attack_sword]="a sword strike to the right. The sword IS in his right hand in this strip (steel blade, gold guard, exactly as in the reference). 0 wind-up: sword drawn back over the shoulder, body leaning back; 1 the strike: sword swung forward and down at its farthest point, body lunging forward; 2 follow-through: sword low in front, body leaning forward; 3 return to a neutral stance holding the sword low."
 [attack_fist]="an unarmed punch to the right, no sword: 0 wind-up: fist pulled back, leaning back; 1 the punch: fist thrust forward at its farthest point, lunging; 2 follow-through leaning forward; 3 return to a neutral stance."
 [die]="falling down after being hit, no sword: 0 hit recoil, body arched back, eyes squeezed shut; 1 sinking to his knees, head down; 2 sitting slumped on the ground; 3 lying flat on his back on the ground, motionless, this is the final pose of the body and it lies low along the ground line."
 [emerge]="climbing up out of the ground at the start of the game: 0 only his hood and both hands are visible over a small mound of soil at the ground line; 1 the upper half of the body is out, arms pushing on the ground; 2 climbing out onto his feet, dusting soil off; 3 standing upright and ready, soil crumbs around the feet."
 [build]="hammering a building: he holds the small hammer from his belt in his right hand. Loop: 0 hammer raised high over the shoulder; 1 hammer swinging down; 2 hammer hitting at chest height in front, body leaning in; 3 hammer lifted back to the middle."
 [carry_walk]="walking right while carrying a heavy box in both arms in front of the chest. DO NOT draw the box or any object: the arms are bent forward in a holding pose with the hands together as if cupping an invisible box at chest height. Loop of four key poses: 0 right leg forward, 1 passing pose body slightly higher, 2 left leg forward, 3 passing pose."
 [loot]="opening a treasure chest in front of him on the right. DO NOT draw the chest or any item. 0 bending forward with both hands reaching out at knee height; 1 hands lifting an invisible lid up in front, leaning in; 2 reaching into the invisible chest, head down; 3 straightening up, both hands raised to the chest holding something small (not drawn), happy face."
)
IDS=${@:-idle}
for id in $IDS; do
  case $id in idle) REFS="$R";; *) REFS="$R $A/hero_idle_v$V.png";; esac
  gen $id "$REFS" "$HEAD ${ACT[$id]}$( [ $id != idle ] && echo ' The second attached image is the idle strip: use it as the scale and ground-line reference.')" &
done
wait
echo DONE

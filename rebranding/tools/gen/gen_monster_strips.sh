#!/bin/bash
# Полосы кадров монстра: сетка 2x2 (как у героя). Запуск: bash tools/gen/gen_monster_strips.sh <имя> <key> <melee|ranged|fast> [v] [px=1536]
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/d6945f1c-fd00-403e-a79e-f106200f409c/scratchpad}
NAME=$1; KEY=${2:-FF00FF}; ATK=${3:-melee}; V=${4:-1}; PX=${5:-1536}
A=out/anim/monsters/$NAME; R=$A/${NAME}_ref.png
gen() { # id prompt
  [ -f "$A/${NAME}_$1_v$V.png" ] && return
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image, square, target ${PX}x${PX} (resize with ImageMagick only if needed, never crop or stretch). PNG. $2 Avoid: text, letters, numbers, labels, grid lines, borders, logos, watermark, photorealism, glossy plastic, pixel art, thick black outlines, ground shadow, scenery, extra characters. Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$A/${NAME}_$1_v$V.png . Do not overwrite existing files. Print the saved path and dimensions." -i "$R" \
  > "$S/${NAME}_$1_v$V.log" 2>&1
}
HEAD="[NIGHT] Animation frames of ONE monster on a flat solid #$KEY background (no gradient, no shadow, no fringe): a 2 x 2 arrangement of four equal square cells (top-left, top-right, bottom-left, bottom-right; the cells are invisible, NOT drawn), frame order: top-left, top-right, bottom-left, bottom-right. In every cell the attached reference monster, facing right, same design, colors, proportions, outline weight and exactly the same scale as in the reference sheet; centered in the cell with its feet/base on the same ground line at 88% of the cell height in all four cells; it never touches or crosses its cell edge. Each frame is a clearly different key pose. Matte hand-painted 3D look, cute-menacing, no gore, no blood. Action:"
case $ATK in
  melee) ATKTXT="a melee attack: frame 1 wind-up, frame 2 the strike at full extension, frame 3 follow-through, frame 4 recovering.";;
  ranged) ATKTXT="aiming and shooting: frame 1 raising the weapon, frame 2 drawing/aiming, frame 3 releasing the shot, frame 4 lowering it (draw no projectile).";;
  fast) ATKTXT="two quick strikes: frame 1 wind-up, frame 2 first strike, frame 3 wind-up again, frame 4 second strike.";;
esac
gen walk "$HEAD moving to the right in a 4-frame cycle (frame 1 and 3 are contact poses, 2 and 4 are passing poses; floating monsters bob up and down)." &
gen attack "$HEAD $ATKTXT" &
gen die "$HEAD dying: frame 1 hit and recoiling, frame 2 collapsing, frame 3 breaking apart or melting, frame 4 a low final corpse pose lying on the ground." &
[ "${SPELL:-0}" = 1 ] && gen spell "$HEAD casting a spell: frame 1 raising the staff, frame 2 gathering red energy, frame 3 releasing the spell with a burst of glow, frame 4 lowering the staff." &
wait
echo DONE

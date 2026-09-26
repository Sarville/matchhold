#!/bin/bash
# Верхняя грань каменного фундамента-капсулы (вид сверху, плиты). Наклон в перспективу делает tools/build_capsules.py.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/8cf97f12-1c34-4a07-9e32-fb51c227da2b/scratchpad}
gen() { # out refs size key prompt
  [ -f "$1" ] && return
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached image is a reference for the stone material and colour only. Target size $3 (if the native size differs, resize the whole picture to FIT INSIDE with ImageMagick and pad with the key colour; NEVER crop, NEVER stretch). PNG. $5 The whole background is a solid flat $4 (no gradient, no shadow); nothing in the artwork is that colour. Avoid: text, people, plants, moss, cast shadow, gloss, photorealism. Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
for v in 1 2; do
gen out/env/capsules/plinth_top_v$v.png out/env/capsules/capsule_stone3_v2.png 1120x240 '#00FF00' "Cozy fantasy game art, warm soft matte hand-painted look, chunky rounded forms. The flat TOP surface of a long stone plinth seen straight from above (top view, no perspective): a horizontal rectangle, about 4.5 times wider than tall, paved with warm grey-beige rectangular stone slabs with thin mortar lines, slightly lighter than the reference front face, a thin chamfered lighter edge all around. The rectangle fills the canvas edge to edge with a small margin. Flat even lighting, no shadow, no text." &
done
wait; echo DONE

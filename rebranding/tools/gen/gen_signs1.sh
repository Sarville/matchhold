#!/bin/bash
# Столбики с табличками по краям мини-фона: справа «Уровень», слева «День + фаза» (солнце/луна). Табличка пустая: число и иконку рисует игра.
# Этап 1: день (2 варианта на каждую). Этап 2 (gen_signs2.sh): ночь по выбранной дневной.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/8cf97f12-1c34-4a07-9e32-fb51c227da2b/scratchpad}
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left, soft warm shadow toward the bottom-right. A thin outline slightly darker than the object own hue, never black. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
gen() { # out refs size key prompt
  [ -f "$1" ] && return
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: the first is the wood-and-brass panel style, the second is the ground with stones and grass; follow them for style, palette and material only. Target size $3 (if the native size differs, resize the whole picture to FIT INSIDE with ImageMagick and pad with the key colour; NEVER crop, NEVER stretch; the subject stays complete with at least 4% empty key-colour margin). PNG. $5 The whole background is a solid flat $4 (no gradient, no shadow, no fringe); nothing in the artwork is that colour. Avoid: people, text, letters, digits, symbols on the board, logos, watermark, UI, photorealism, gloss, lens flare, pixel art, thick black outlines, buildings, trees, cast shadow, extra objects. Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
R="out/icons/hud/panel_plate_day_v1.png out/env/ground/keyed/ground_strip_v2.png"
POST='One single wooden signpost seen straight from the front, standing upright, centered, base touching the bottom of the subject: a thick chestnut wooden post with a small cap on top and a short crossarm near the top; at its foot a few small stones and grass tufts and a little sandy earth like in the second reference. From the crossarm hangs a board on two short brass chains. The board is chestnut wood with a thin brass rim and tiny brass rivets like the first reference. The whole subject is tall: about 1.8 times taller than wide, the board takes the upper 45% of the height and about 90% of the width.'
for v in 1 2; do
gen out/env/signs/sign_level_day_v$v.png "$R" 768x1024 '#FF00FF' "$DAY $POST On the board face there is ONE large empty cream-parchment plaque (light, nearly square, slightly inset, thin brass rim) meant for a big number, nothing else on the board. Empty: no symbols, no digits." &
gen out/env/signs/sign_day_day_v$v.png "$R" 768x1024 '#FF00FF' "$DAY $POST On the board face, on the left a small round empty socket with a brass ring and a dark recessed interior (for an icon), and to the right of it a large empty cream-parchment plaque (light, wide, slightly inset, thin brass rim) meant for a number. Both empty: no symbols, no digits." &
done
wait; echo DONE

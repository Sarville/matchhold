#!/bin/bash
# Оставшиеся иконки: reset_board, state_frozen, золотые сердца, солнце/луна, эмблема и значок.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/f6ddb6fb-bf5a-42c9-8333-431a964eaff3/scratchpad}
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left. A thin outline slightly darker than the object own hue, never black. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light. Thin outline slightly darker than the object own hue, never black.'
KEY='The whole background is a solid flat #FF00FF (no gradient, no shadow, no fringe); nothing else in the artwork is pink or magenta. One object only, centered, no ground shadow, no text.'
NEG='Avoid: text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them where the prompt says, otherwise use them for style, palette and material only. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $4 $KEY $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
K=out/icons/keyed; H=out/icons/hud; P=out/icons/spells; B=out/icons/brand; SK=out/env/sky
D=refs/ref-day-layout.png; N=refs/ref-night-layout.png
gen $P/spell_reset_board_v1.png "$K/spell_haste_v1.png $K/spell_phase_change_v1.png" 512x512 "$DAY A single game spell icon in exactly the same style, size and framing as the attached spell icons: two curved arrows chasing each other in a circle around a tiny sand-colored game tile, warm gold. Fills about 70% of the canvas." &
gen $P/state_frozen_v1.png "$K/spell_freeze_time_v1.png" 512x512 "$DAY A single game state icon in exactly the same style, size and framing as the attached icon: a cluster of blue ice crystals frozen in a block, pale blue and white, simple bold shape. Fills about 70% of the canvas." &
gen $H/heartbig_socket_day_v1.png "$K/heart_socket_day_v1.png $D" 512x512 "$DAY The same round ring holding an EMPTY heart as the first attached image (identical outline and proportions), but the ring is polished gold with a brass rim, slightly richer, a small leaf on the left; inside the ring the pale empty recessed heart-shaped hollow, cream colored. Fills about 90% of the canvas." &
wait
gen $H/heartbig_socket_night_v1.png "$H/heartbig_socket_day_v1.png $K/heart_socket_night_v1.png" 512x512 "$NIGHT The exact same gold ring with an empty heart as the first attached day image (identical outline and proportions), but as a dark bronze ring with a faint warm glow on the rim; the recessed heart-shaped hollow inside is dark slate. Fills about 90% of the canvas." &
gen $H/heartbig_fill_v1.png "$H/heartbig_socket_day_v1.png $K/heart_fill_v1.png" 512x512 "$DAY A single game HUD icon: a plump golden heart exactly the shape, size and position of the empty cream heart-shaped hollow inside the attached ring, soft matte gold, two tiny sparkles, NO ring, the heart only, on the same 512x512 canvas so it lies exactly over the hollow." &
gen $SK/sky_sun_v1.png "$D" 512x512 "$DAY A soft round sun disc for a sky: warm cream-yellow disc with a gentle darker golden edge and very soft hand-painted glow around it, seen from the front, no face, no rays like a spiky star, just a round warm sun with a subtle halo. Fills about 80% of the canvas." &
gen $SK/sky_moon_v1.png "$N" 512x512 "$NIGHT A round full moon disc for a night sky: pale cool blue-white with soft matte grey-blue craters, a gentle cool halo, seen from the front, no face. Fills about 80% of the canvas." &
gen $B/logo_emblem_v1.png "$D $N" 1024x1024 "$DAY A heraldic emblem for a village-building game: a small round-towered stone castle keep over two crossed items (a sword and a builder's hammer), a blue banner with a golden fleur-de-lis flying from the tower, warm gold and blue accents, front view, chunky rounded forms. Fills about 80% of the canvas." &
gen $B/logo_emblem_v2.png "$D $N" 1024x1024 "$DAY A heraldic emblem for a village-building game: a compact shield shape with a small round-towered castle keep on it, a sword and a builder's hammer crossed behind the shield, a blue pennant with a golden fleur-de-lis on the tower, warm gold and blue accents, front view, chunky rounded forms. Fills about 80% of the canvas." &
wait
echo DONE

#!/bin/bash
cd /home/user/projects/matchhold/rebranding || exit 1
S=/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left. A thin outline slightly darker than the object own hue, never black. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light. Thin outline slightly darker than the object own hue, never black.'
KEY='The whole background is a solid flat #FF00FF (no gradient, no shadow, no fringe); nothing else in the artwork is pink or magenta. One object only, centered, no ground shadow, no text.'
NEG='Avoid: text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them where the prompt says, otherwise use them for style, palette and material only. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $4 $KEY $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
H=out/icons/hud; L=out/icons/loot; P=out/icons/spells
D=refs/ref-day-layout.png; N=refs/ref-night-layout.png
gen $H/heart_socket_day_v1.png $D 512x512 "$DAY A single game HUD icon: a round ring holding an EMPTY heart: warm chestnut wood ring with a brass rim and a small leaf on the left; inside the ring a pale, empty, slightly recessed heart-shaped hollow, cream colored. Fills about 90% of the canvas." &
gen $H/slot_ring_day_v1.png $N 512x512 "$DAY A single game HUD icon: an empty round slot: gold ring with tiny gold beads at the bottom, as in the attached reference (bottom-right panel), empty dark inset centre. Fills about 90% of the canvas." &
gen $H/inventory_plank_day_v1.png $N 1536x512 "$DAY A horizontal plank plate that holds three round slots, wood and brass, with three empty round hollows evenly spaced, in the style of the attached reference bottom-right panel; hollows empty. Fills the canvas width with a small margin." &
gen $H/bar_frame_day_v1.png $D 1536x512 "$DAY A horizontal empty trough frame, wood with brass rims, rounded ends, dark empty inset; no fill, no icon, no text. Fills the canvas width with a small margin." &
gen $L/loot_health_potion_v1.png $N 512x512 "$DAY A single game item icon: a round-bottom glass flask with a cork, filled with glowing red liquid, tiny bubbles, like the red potion in the attached reference. Fills about 70% of the canvas." &
gen $L/loot_mana_potion_v1.png $N 512x512 "$DAY A single game item icon: a round-bottom glass flask with a cork, filled with glowing blue liquid, tiny bubbles, like the blue potion in the attached reference. Fills about 70% of the canvas." &
gen $P/spell_haste_v1.png $N 512x512 "$DAY A single game spell icon: a small winged boot, light blue speed swooshes. Fills about 70% of the canvas." &
gen $P/spell_freeze_time_v1.png $N 512x512 "$DAY A single game spell icon: a pocket stopwatch covered in ice crystals, pale blue. Fills about 70% of the canvas." &
wait
gen $P/spell_phase_change_v1.png $N 512x512 "$DAY A single game spell icon: a sun and a crescent moon overlapping, warm gold and cool blue. Fills about 70% of the canvas." &
gen $H/heart_fill_v1.png "$H/heart_socket_day_v1.png" 512x512 "$DAY A single game HUD icon: a plump red heart exactly the shape, size and position of the empty cream heart-shaped hollow inside the attached ring, soft matte, NO ring, the heart only, on the same 512x512 canvas so it lies exactly over the hollow." &
gen $H/heart_socket_night_v1.png "$H/heart_socket_day_v1.png $N" 512x512 "$NIGHT The exact same round ring holding an empty heart as the first attached day image: identical outline and proportions, but built from dark stone with an iron rim and a small dark leaf; the recessed heart-shaped hollow inside is dark slate. Fills about 90% of the canvas." &
gen $H/slot_ring_night_v1.png "$H/slot_ring_day_v1.png $N" 512x512 "$NIGHT The exact same empty round slot as the first attached day image (identical outline and proportions), but a stone ring with iron studs and beads, empty dark inset centre. Fills about 90% of the canvas." &
gen $H/inventory_plank_night_v1.png "$H/inventory_plank_day_v1.png $N" 1536x512 "$NIGHT The exact same horizontal plank plate with three round hollows as the first attached day image (identical outline, hollow positions and proportions), but stone and iron; hollows empty." &
gen $H/bar_frame_night_v1.png "$H/bar_frame_day_v1.png $N" 1536x512 "$NIGHT The exact same horizontal empty trough frame as the first attached day image (identical outline and proportions), but stone with iron rims; dark empty inset; no fill." &
wait
echo DONE

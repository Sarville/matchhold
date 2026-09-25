#!/bin/bash
cd /home/user/projects/matchhold/rebranding || exit 1
S=/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light and a gentle glow on key details.'
NEG='Avoid: text, letters, numbers, logos, watermark, signature, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage, characters, birds, frame, pink or magenta colors inside the artwork.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them where the prompt says so, otherwise use them for mood, palette and material only. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $4 $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
E=out/env
SCENE="the same scene as the attached full background (windmill on the left hill, cottages left and right, dirt road, rolling hills, forest, distant mountains, small lake)"
# ждём дальний слой дня
for i in $(seq 1 120); do [ -s $E/bg/bg_s1_far_day_land_v1.png ] && break; sleep 10; done
sleep 5
MIDD="[DAY] MIDDLE layer at the SAME LEVEL AS THE GAME BOARD, on a solid flat #FF00FF background (no gradient, no fringe), wide 2:1, to sit over the first attached far layer. Ground-level side scenery seen straight on, at the same eye level as a board in the center: on the LEFT side and on the RIGHT side (each occupying only the outer 25-28% of the width) one small cluster: one or two cottages (thatched and red roofs, cream walls, wooden fences), a short piece of dirt road curving off toward the edge, grass tufts, bushes, flowers and a small tree. Buildings stand on a ground line at about 70% of the height and are about 25-30% of the canvas height tall. A soft grassy ground strip fills the bottom 28% of the canvas across the full width. Everything above the roofs and tree silhouettes, and the entire central 44% of the width above the grass strip, is solid #FF00FF (sky is not drawn). This layer must NOT distract from a game board in the center: muted, slightly desaturated, hazy, LOW contrast, simplified details, gentle soft focus, no bright accents. Keep crisp clean silhouette edges against the magenta. Same architecture and style as the attached full background."
gen $E/bg/bg_s1_mid_day_land_v1.png "$E/bg/bg_s1_far_day_land_v1.png $E/bg/bg_s1_day_land_v2.png" 4320x2160 "$DAY $MIDD" &
FARN="[NIGHT] The same FAR background layer as the first attached day far layer (same mountains, hills, lake in the same places), now at night: large moon, deep indigo sky with a few stars, blue mist. Fully opaque, no buildings, no foreground, very soft and hazy, low contrast. Mood and palette from the second attached image."
gen $E/bg/bg_s1_far_night_land_v1.png "$E/bg/bg_s1_far_day_land_v1.png refs/ref-night-layout.png" 4320x2160 "$NIGHT $FARN" &
wait
MIDN="[NIGHT] The same MIDDLE layer as the first attached day mid layer (same cottages, road, plants in the same places), now at night: dark pine silhouettes, warm lit windows and lanterns, blue mist. Keep the solid flat #FF00FF background exactly where it is in the day layer (sky and the central 44% empty above the grass strip). Muted, low contrast, hazy, must NOT distract from a game board in the center. The second attached image is the night far layer it sits on."
gen $E/bg/bg_s1_mid_night_land_v1.png "$E/bg/bg_s1_mid_day_land_v1.png $E/bg/bg_s1_far_night_land_v1.png" 4320x2160 "$NIGHT $MIDN"
echo DONE

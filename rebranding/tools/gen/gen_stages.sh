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
stage() { # N far_scene mid_scene
N=$1; FAR_SC=$2; MID_SC=$3
PREVFAR=$E/bg/bg_s1_far_day_land_v1.png
FARD="[DAY] FAR background layer, wide 2:1, fully opaque, stage $N: soft sky with gentle clouds, warm toward the horizon, distant blue mountains and far hills in haze. $FAR_SC. ONLY the far distance: NO near buildings, NO foreground, NO bushes. The horizon is at about 62% of the height. Very soft depth-of-field, hazy and low-contrast. The central 40% of the width is calm. Same painting style, sky and mountains family as the first attached far layer (stage 1), the scene is a grown-up version of it."
gen $E/bg/bg_s${N}_far_day_land_v1.png "$PREVFAR refs/ref-day-layout.png" 4320x2160 "$DAY $FARD"
MIDD="[DAY] MIDDLE layer at the SAME LEVEL AS THE GAME BOARD, on a solid flat #FF00FF background (no gradient, no fringe), wide 2:1, stage $N, to sit over the first attached far layer. Ground-level side scenery seen straight on, at the same eye level as a board in the center: on the LEFT side and on the RIGHT side (each only the outer 25-28% of the width) one small cluster: $MID_SC. Grass tufts, bushes and flowers, a short piece of road curving off toward the edge. Buildings stand on a ground line at about 70% of the height and are about 25-30% of the canvas height tall. A soft grassy ground strip fills the bottom 28% of the canvas across the full width. Everything above the roofs and tree silhouettes, and the entire central 44% of the width above the grass strip, is solid #FF00FF (sky is not drawn). Must NOT distract from a game board in the center: muted, slightly desaturated, hazy, LOW contrast, simplified details, gentle soft focus, no bright accents. Crisp clean silhouette edges against the magenta. Same style and ground strip look as the second attached image (stage 1 mid layer)."
gen $E/bg/bg_s${N}_mid_day_land_v1.png "$E/bg/bg_s${N}_far_day_land_v1.png $E/bg/bg_s1_mid_day_land_v1.png" 4320x2160 "$DAY $MIDD" &
FARN="[NIGHT] The same FAR background layer as the first attached day far layer (same mountains, hills, features in the same places), now at night: large moon, deep indigo sky with a few stars, blue mist, warm tiny lights where the day layer has settlements. Fully opaque, no near buildings, no foreground, very soft and hazy, low contrast. Mood and palette from the second attached image (stage 1 night far layer)."
gen $E/bg/bg_s${N}_far_night_land_v1.png "$E/bg/bg_s${N}_far_day_land_v1.png $E/bg/bg_s1_far_night_land_v1.png" 4320x2160 "$NIGHT $FARN" &
wait
MIDN="[NIGHT] The same MIDDLE layer as the first attached day mid layer (same buildings, road, plants in the same places), now at night: dark silhouettes, warm lit windows and lanterns, blue mist. Keep the solid flat #FF00FF background exactly where it is in the day layer (sky and the central 44% empty above the grass strip). Muted, low contrast, hazy, must NOT distract from a game board in the center. The second attached image is the night far layer it sits on. The third is the stage 1 night mid layer for style."
gen $E/bg/bg_s${N}_mid_night_land_v1.png "$E/bg/bg_s${N}_mid_day_land_v1.png $E/bg/bg_s${N}_far_night_land_v1.png $E/bg/bg_s1_mid_night_land_v1.png" 4320x2160 "$NIGHT $MIDN"
}
stage 2 "A larger village: more cottages on hills, a river with a stone bridge, a small stone watchtower far away, fields and a windmill in the distance" "two stone-and-timber houses with red roofs, a short piece of a wooden fence and a small stone bridge edge over a stream" &
stage 3 "A town: stone walls and towers with red and blue roofs in the distance, a river with a bridge, a castle on a hill far away" "a piece of a stone town wall with a small tower, one or two tall houses with red and blue roofs, a cobbled road" &
stage 4 "A capital: a huge castle on a cliff with banners far away, waterfalls, an arched aqueduct, city buildings to the horizon, golden light" "a stone castle gatehouse corner with a banner, a tall stone house with blue roof, cobbled road and a stone planter with flowers" &
wait
echo DONE

#!/bin/bash
cd /home/user/projects/matchhold/rebranding || exit 1
S=/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light and a gentle glow on key details.'
NEG='Avoid: text, letters, numbers, logos, watermark, signature, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage, characters, birds, frame, pink or magenta colors inside the artwork.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=medium --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them where the prompt says so, otherwise use them for mood, palette and material only. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $4 $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
E=out/env
SCENE="the same scene as the attached full background (windmill on the left hill, cottages left and right, dirt road, rolling hills, forest, distant mountains, small lake)"
# ---------- ночная тонкая рамка ----------
FRAMEN="The exact same square game-board frame as the first attached image (the day frame): identical outline, identical thin uniform thickness on all four sides, identical square inner opening, identical ivy placement, identical corner brackets, but built from cool blue-grey cut stone blocks with mortar lines and worn edges, ivy darker and slightly bluish, faint moonlit rim light on the top-left edges, small dark-iron corner brackets. Keep the top beam bare and flat. Fill the opening and everything outside the frame with solid flat #FF00FF (no gradient, no shadow, no fringe). Matte, no gloss. No tiles, no buildings, no people, no text."
for v in 1 2 3; do gen $E/frame/frame_night_thin_v$v.png "$S/frame_day_thin_fit_key.png refs/ref-night-layout.png" 2048x2048 "$NIGHT $FRAMEN" & done
# ---------- этап A: дальний слой день, передний слой день ----------
FARD="[DAY] FAR background layer, wide 2:1, fully opaque: soft sky with gentle clouds, warm toward the horizon, distant blue mountains, far rolling hills and tree lines in haze, a hint of a small lake, $SCENE but ONLY the far distance: NO buildings, NO windmill, NO near hills, NO bushes, NO foreground. The horizon is at about 62% of the height, the lower part is soft hazy far hills. Very soft depth-of-field, everything hazy and low-contrast. The central 40% of the width is calm."
gen $E/bg/bg_s1_far_day_land_v1.png "$E/bg/bg_s1_day_land_v2.png refs/ref-day-layout.png" 4320x2160 "$DAY $FARD" &
FGD="[DAY] Out-of-focus FOREGROUND layer on a solid flat #FF00FF background (no gradient, no fringe), wide 2:1: large blurry sage-green leaves and a leafy branch in the top-left corner, ivy and a few small white flowers, mossy stones and grass tufts in the bottom-left and bottom-right corners. Strong depth-of-field blur (bokeh), soft edges. Everything in the central 50% of the canvas is completely solid #FF00FF. Nothing else."
gen $E/fg/fg_day_land_v1.png "$E/bg/bg_s1_day_land_v2.png" 4320x2160 "$DAY $FGD" &
FGN="[NIGHT] Out-of-focus FOREGROUND layer on a solid flat #FF00FF background (no gradient, no fringe), wide 2:1: dark blurry leaves top-left, ferns, stone ruins with an iron lantern and a burning torch in the bottom corners, warm orange glow spilling softly from the torches. Strong depth-of-field blur (bokeh), soft edges. Everything in the central 50% of the canvas is completely solid #FF00FF. Nothing else."
gen $E/fg/fg_night_land_v1.png "$E/bg/bg_s1_night_land_v1.png refs/ref-night-layout.png" 4320x2160 "$NIGHT $FGN" &
wait
# ---------- этап B: средний слой день (по дальнему) ----------
MIDD="[DAY] MIDDLE-ground layer on a solid flat #FF00FF background (no gradient, no fringe), wide 2:1, to be placed over the first attached far layer, $SCENE: only the middle distance: green hills with the dirt road, the windmill, the cottages, trees, fences and stone walls placed ONLY in the far left and far right thirds. Everything above the hill/tree/roof silhouettes is solid #FF00FF (sky is not drawn). The central 40% of the width is solid #FF00FF except a very low, soft grassy hill line along the bottom 15% of the canvas spanning the full width. This layer must NOT distract from a game board that will sit in the center: muted, slightly desaturated, hazy, LOW contrast, simplified details, gently soft focus, no bright accents, no saturated colors. Keep clean crisp silhouette edges against the magenta."
gen $E/bg/bg_s1_mid_day_land_v1.png "$E/bg/bg_s1_far_day_land_v1.png $E/bg/bg_s1_day_land_v2.png" 4320x2160 "$DAY $MIDD"
# ---------- этап C: ночь дальний и средний ----------
FARN="[NIGHT] The same FAR background layer as the first attached day far layer (same mountains, hills, lake in the same places), now at night: large moon, deep indigo sky with a few stars, blue mist. Fully opaque, no buildings, no foreground, very soft and hazy, low contrast. Mood and palette from the second attached image."
gen $E/bg/bg_s1_far_night_land_v1.png "$E/bg/bg_s1_far_day_land_v1.png refs/ref-night-layout.png" 4320x2160 "$NIGHT $FARN"
MIDN="[NIGHT] The same MIDDLE-ground layer as the first attached day mid layer (same windmill, cottages, road, hills in the same places), now at night: dark pine silhouettes, warm lit windows and lanterns, blue mist. Keep the solid flat #FF00FF background exactly where it is in the day layer (sky and the central 40% empty). Muted, low contrast, hazy, must NOT distract from a game board in the center. The second attached image is the night far layer it sits on."
gen $E/bg/bg_s1_mid_night_land_v1.png "$E/bg/bg_s1_mid_day_land_v1.png $E/bg/bg_s1_far_night_land_v1.png" 4320x2160 "$NIGHT $MIDN"
echo DONE

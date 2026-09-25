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
# ---- тест настоящей прозрачности: передний слой ----
FGD="[DAY] Out-of-focus FOREGROUND framing layer with a genuinely TRANSPARENT background (real alpha channel, no colored background, no magenta), wide 2:1. Natural organic vignette made of blurry sage-green leaves, a leafy branch, ivy, a few small white flowers, grass tufts and mossy stones, hugging the top-left corner, the bottom-left and bottom-right corners and the left and right edges. The foliage trails off NATURALLY toward the center: leaves and stems end with their own soft rounded organic tips and thin tapering shapes, fading out gradually. There must be NO straight vertical or horizontal cut edges anywhere and no rectangular boundary: every foliage shape ends with its own natural outline. The large middle area of the canvas has no content at all (fully transparent). Strong depth-of-field blur (bokeh), soft edges."
gen $E/fg/fg_day_land_v2.png "$E/bg/bg_s1_day_land_v2.png" 4320x2160 "$DAY $FGD" &
FGN="[NIGHT] Out-of-focus FOREGROUND framing layer with a genuinely TRANSPARENT background (real alpha channel, no colored background, no magenta), wide 2:1. Natural organic vignette made of dark blurry leaves and ferns at the top-left, stone ruins with an iron lantern and a burning torch in the bottom corners, warm orange glow spilling softly from the torches. The foliage and ruins trail off NATURALLY toward the center with their own soft organic outlines. There must be NO straight vertical or horizontal cut edges anywhere and no rectangular boundary. The large middle area of the canvas has no content at all (fully transparent). Strong depth-of-field blur (bokeh), soft edges."
gen $E/fg/fg_night_land_v2.png "$E/bg/bg_s1_night_land_v1.png refs/ref-night-layout.png" 4320x2160 "$NIGHT $FGN" &
# ---- дальний слой в порте: день, затем ночь, по 4 этапам ----
farport() {
N=$1
FPD="[DAY] Vertical 1:2 version of the attached far background layer (stage $N): the same far scene recomposed for a tall phone screen: soft sky with gentle clouds in the upper part, distant mountains and far hazy hills with the same features in the same relation, the horizon at about 62% of the height, soft hazy far hills and meadow haze below. Fully opaque. ONLY the far distance: no near buildings, no foreground, no bushes. Very soft, hazy, low contrast. Same painting style and colors."
gen $E/bg/bg_s${N}_far_day_port_v1.png "$E/bg/bg_s${N}_far_day_land_v1.png" 1440x2880 "$DAY $FPD"
FPN="[NIGHT] The same far background layer as the first attached day portrait (same features in the same places), now at night: large moon, deep indigo sky with a few stars, blue mist, tiny warm lights where the day layer has settlements. Fully opaque, no near buildings, no foreground. The second attached image is the night land far layer of the same stage for palette and mood. Very soft, hazy, low contrast."
gen $E/bg/bg_s${N}_far_night_port_v1.png "$E/bg/bg_s${N}_far_day_port_v1.png $E/bg/bg_s${N}_far_night_land_v1.png" 1440x2880 "$NIGHT $FPN"
}
for N in 1 2 3 4; do farport $N & done
wait
echo DONE

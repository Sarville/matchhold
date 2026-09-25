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
midport() { # N scene
N=$1; MID_SC=$2
MPD="[DAY] MIDDLE layer for a tall phone screen (vertical 1:2) with a genuinely TRANSPARENT background (real alpha channel, no colored background, no magenta), stage $N. It sits over the first attached far portrait layer, with the same scene and style as the second attached image (the wide landscape middle layer of the same stage). Ground-level scenery seen straight on, ONLY in the bottom 30% of the canvas: a soft grassy ground strip across the full width, and on the LEFT and on the RIGHT side (each only the outer 30% of the width) one small cluster: $MID_SC. Grass tufts, bushes and flowers, a short piece of road curving off toward the edge. Buildings stand on a ground line at about 88% of the height and are about 12% of the canvas height tall. Everything above the buildings and grass is fully transparent, and the central 40% of the width above the grass strip is fully transparent. Must NOT distract from a game board above it: muted, slightly desaturated, hazy, LOW contrast, simplified details, gentle soft focus, no bright accents. Clean silhouettes with natural soft edges, no straight cut lines."
gen $E/bg/bg_s${N}_mid_day_port_v1.png "$E/bg/bg_s${N}_far_day_port_v1.png $E/bg/bg_s${N}_mid_day_land_v1.png" 1440x2880 "$DAY $MPD"
MPN="[NIGHT] The same MIDDLE layer as the first attached day portrait (same buildings, road, plants in the same places), now at night: dark silhouettes, warm lit windows and lanterns, blue mist, with a genuinely TRANSPARENT background exactly where the day layer is transparent (real alpha channel, no magenta). The second attached image is the night far portrait layer it sits on; the third is the wide night middle layer of the same stage for style. Muted, low contrast, hazy, must NOT distract from a game board above it. Natural soft edges, no straight cut lines."
gen $E/bg/bg_s${N}_mid_night_port_v1.png "$E/bg/bg_s${N}_mid_day_port_v1.png $E/bg/bg_s${N}_far_night_port_v1.png $E/bg/bg_s${N}_mid_night_land_v1.png" 1440x2880 "$NIGHT $MPN"
}
midport 1 "one or two cottages (thatched and red roofs, cream walls, wooden fences), a small tree" &
midport 2 "two stone-and-timber houses with red roofs, a short wooden fence and a small stone bridge edge over a stream" &
midport 3 "a piece of a stone town wall with a small tower, one or two tall houses with red and blue roofs, a cobbled road" &
midport 4 "a stone castle gatehouse corner with a banner, a tall stone house with blue roof, cobbled road and a stone planter with flowers" &
FGDP="[DAY] Out-of-focus FOREGROUND framing layer for a tall phone screen (vertical 1:2) with a genuinely TRANSPARENT background (real alpha channel, no colored background, no magenta). Natural organic vignette made of blurry sage-green leaves, a leafy branch, ivy, a few small white flowers, grass tufts and mossy stones, hugging the top-left and top-right corners and the bottom-left and bottom-right corners and bottom edge. The foliage trails off NATURALLY: every leaf and stem ends with its own soft rounded organic tip, NO straight vertical or horizontal cut edges anywhere. The whole middle band of the canvas (from about 22% to 78% of the height) has no content at all (fully transparent). Strong depth-of-field blur (bokeh), soft edges."
gen $E/fg/fg_day_port_v1.png "$E/fg/fg_day_land_v2.png" 1440x2880 "$DAY $FGDP" &
FGNP="[NIGHT] Out-of-focus FOREGROUND framing layer for a tall phone screen (vertical 1:2) with a genuinely TRANSPARENT background (real alpha channel, no colored background, no magenta). Dark blurry leaves and ferns at the top corners, stone ruins with an iron lantern and a burning torch in the bottom corners, warm orange glow spilling softly from the torches. Everything trails off NATURALLY with its own soft outline, NO straight cut edges. The whole middle band of the canvas (from about 22% to 78% of the height) has no content at all (fully transparent). Strong depth-of-field blur (bokeh), soft edges."
gen $E/fg/fg_night_port_v1.png "$E/fg/fg_night_land_v2.png" 1440x2880 "$NIGHT $FGNP" &
wait
echo DONE

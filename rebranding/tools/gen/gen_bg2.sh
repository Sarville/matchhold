#!/bin/bash
cd /home/user/projects/matchhold/rebranding || exit 1
S=/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light and a gentle glow on key details.'
NEG='Avoid: text, letters, numbers, logos, watermark, signature, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, cropped edges, sharp foreground details, multiple views, collage, characters, birds, frame.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=medium --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them where the prompt says so, otherwise use them for mood, palette and material only, do not copy their composition. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG, opaque. $4 $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
DAYLAND=out/env/bg/bg_s1_day_land_v2.png
NIGHTLAND="[NIGHT] Same scene as the first attached day background (same landmarks in the same places: windmill, cottages, dirt road, hills, distant mountains), now at night: large moon, deep indigo sky with a few stars, warm lit windows and torches, blue mist, dark pine silhouettes. Soft depth-of-field as in the day version. Mood and palette from the second attached image. Keep the central 40% of the width calm and dark low-contrast. No characters, no text, no frame."
DAYPORT="[DAY] Vertical 9:19.5 version of the first attached background: the same scene and landmarks, recomposed for a tall phone screen. Keep the vertical band from 25% to 75% of the height calm, low-contrast and empty (soft sky, haze, distant hills only). Put the sky and the skyline (windmill, roofs, mountains) in the top 25% and the foreground meadow, road and flowers in the bottom 25%. Same soft depth-of-field. No characters, no text, no frame."
NIGHTPORT="[NIGHT] Vertical 9:19.5 version of the first attached night background: the same night scene and landmarks, recomposed for a tall phone screen, matching the composition of the second attached day portrait image. Keep the vertical band from 25% to 75% of the height calm, low-contrast and empty (soft dark sky, mist, distant hills only). Sky, moon and skyline in the top 25%, foreground meadow and road in the bottom 25%. Same soft depth-of-field. No characters, no text, no frame."
gen out/env/bg/bg_s1_night_land_v1.png "$DAYLAND refs/ref-night-layout.png" 3840x2160 "$NIGHT $NIGHTLAND" &
gen out/env/bg/bg_s1_day_port_v1.png "$DAYLAND" 1440x3120 "$DAY $DAYPORT" &
wait
gen out/env/bg/bg_s1_night_port_v1.png "out/env/bg/bg_s1_night_land_v1.png out/env/bg/bg_s1_day_port_v1.png" 1440x3120 "$NIGHT $NIGHTPORT"
echo DONE

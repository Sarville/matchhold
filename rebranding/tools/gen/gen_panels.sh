#!/bin/bash
cd /home/user/projects/matchhold/rebranding || exit 1
S=/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad
DAY='Cozy fantasy village match-3 game art. Warm, soft, matte hand-painted 3D look: chunky rounded forms, soft ambient occlusion, gentle gradients, NO glossy plastic highlights, NO specular shine. Warm afternoon light from the top-left. A thin outline slightly darker than the object own hue, never black. Palette: warm sand beige, honey gold, chestnut brown, sage green, muted terracotta, cream white.'
NIGHT='Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light. Thin outline slightly darker than the object own hue, never black.'
KEY='The whole background is a solid flat #FF00FF (no gradient, no shadow, no fringe); nothing else in the artwork is pink or magenta. One object only, centered, no ground shadow, no text.'
NEG='Avoid: text, letters, numbers, logos, watermark, UI overlay, photorealism, harsh gloss, lens flare, pixel art, thick black outlines, extra objects, multiple views, collage.'
gen() { # out refs size prompt
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=medium --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached images are references: follow them where the prompt says, otherwise use them for style, palette and material only. Target size $3 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $4 $KEY $NEG Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i $2 \
  > "$S/$(basename $1).log" 2>&1
}
H=out/icons/hud
PLD="$DAY The EXACT same plank plate as the first attached image (the inventory panel): identical wood planks, brass corner brackets with rivets, brass edge, proportions, lighting and canvas size, but with NO round hollows at all: a plain flat wooden center between the corner brackets. The plate fills the canvas width with the same small margin. A single object."
gen $H/panel_plate_day_v1.png "$H/inventory_plank_day_v1.png" 1536x512 "$PLD" &
VD="$DAY A single ivy vine garland meant to be laid over a tall narrow panel: a slender brown-green stem with sage-green ivy leaves winding in a gentle S-curve from the top to the bottom of a tall 1:3 canvas, leaves a bit denser near the top and the bottom, some leaves and tendrils reaching past the left and right edges of the vine, natural organic outline. Same ivy leaf style and colors as in the attached wooden frame. No panel, no frame, only the vine."
gen $H/vine_wrap_day_v1.png "$H/../../env/frame/frame_day_thin_v2.png" 512x1536 "$VD" &
wait
PLN="$NIGHT The exact same plank plate as the first attached day plate (identical outline, proportions and canvas size), but built from stone and iron like the second attached image (the night inventory panel), with NO round hollows: a plain flat stone center between the iron corner brackets. A single object."
gen $H/panel_plate_night_v1.png "$H/panel_plate_day_v1.png $H/inventory_plank_night_v1.png" 1536x512 "$PLN" &
VN="$NIGHT The same ivy vine garland as the attached day vine (same shape, same curve, same leaf positions), now at night: darker blue-green leaves with a faint cool moonlit rim light, a dark stem. Only the vine, no panel."
gen $H/vine_wrap_night_v1.png "$H/vine_wrap_day_v1.png" 512x1536 "$VN" &
wait
echo DONE

#!/bin/bash
# A3: реф-листы оставшихся 11 монстров, 1 вариант каждый (без гейта, по решению пользователя). Запуск из rebranding/.
cd /home/user/projects/matchhold/rebranding || exit 1
S=${S:-/tmp/claude-1000/-home-user-projects-matchhold/d6945f1c-fd00-403e-a79e-f106200f409c/scratchpad}
mkdir -p "$S"
NIGHT='[NIGHT] Cozy fantasy match-3 game art at night. Same warm, soft, matte hand-painted 3D look as the day art (chunky rounded forms, soft ambient occlusion, NO glossy plastic highlights). Deep indigo and navy shadows, cool moonlight from the top-left, warm torch-orange accents, soft rim light and a gentle glow on key details. Thin outline slightly darker than the object own hue, never black. Clean, readable silhouette against dark backgrounds.'
gen() { # out size key brief
  A=$(dirname "$1"); mkdir -p "$A"
  [ -f "$1" ] && return
  codex exec -m gpt-5.6-terra -c model_reasoning_effort=low --sandbox workspace-write \
  "Use the built-in image_gen tool (imagegen skill) to generate ONE image. The attached references are for overall style/lighting/matte look only (first: layout reference; second and third: two already-approved monsters in this same game, for palette richness and finish quality), not for this character's own design. Target size $2 (resize/cover-crop with ImageMagick if the native size differs, no stretching). PNG. $NIGHT Monster character reference sheet on a flat solid #$3 background (no gradient, no shadow, no fringe): $4. Three poses side by side with clear gaps, all facing right, all the same scale and the same ground line: neutral standing, mid-move, and an attack pose. Chunky rounded shapes, matte hand-painted 3D look, same outline weight in every pose, readable silhouette. Cute-menacing, no gore, no blood. Avoid: text, letters, numbers, labels, grid, logos, watermark, photorealism, glossy plastic, pixel art, thick black outlines, ground shadow, background scenery, extra characters, colour matching the key #$3 anywhere on the character. Save the final PNG to exactly: /home/user/projects/matchhold/rebranding/$1 . Do not overwrite existing files. Print the saved path and dimensions." -i refs/ref-night-layout.png out/anim/monsters/zombie/zombie_ref.png out/anim/monsters/skeleton/skeleton_ref.png \
  > "$S/$(basename "$A")_ref.log" 2>&1
}
# имя|класс(S 2304x768 / L 3072x1024)|ключ|бриф
ITEMS=(
"hauntedArmour|L|FF00FF|an empty suit of medieval armor with a big sword floating slightly above the ground, glowing green-blue eyes in the helmet"
"demon|L|00FFFF|a large horned demon, dark red skin, bat wings folded, small flames around the horns, glowing orange eyes"
"rat|S|FF00FF|a big brown rat with a long tail, red glowing eyes, low to the ground"
"spider|L|FF00FF|a large dark spider with long legs, six red eyes, low and wide"
"waterElemental|L|FF00FF|a living blob of blue water with two bright eyes, drips and small waves at the base"
"imp|S|00FFFF|a small red imp with tiny bat wings, pointed tail and horns, a mischievous grin, hovering slightly"
"lizardman|S|FF00FF|a green lizardman archer with a short bow, scaly skin, yellow eyes, tail"
"fireElemental|S|00FFFF|a living flame with a small face, orange and yellow, a lick of fire for arms"
"warlock|S|00FF00|a hooded dark warlock with a gnarled staff, violet magic glowing under the hood"
"earthElemental|L|FF00FF|a big moss-covered stone golem, glowing green eyes, heavy fists"
"lich|L|00FF00|a crowned skeletal lich in tattered dark robes, a staff with a red crystal, glowing red eyes, hovering above the ground"
)
n=0
for it in "${ITEMS[@]}"; do
  IFS='|' read -r name cls key brief <<<"$it"
  sz=$([ "$cls" = L ] && echo 3072x1024 || echo 2304x768)
  while (( $(jobs -r | wc -l) >= 6 )); do sleep 3; done
  gen "out/anim/monsters/$name/${name}_ref_v1.png" "$sz" "$key" "$brief" &
done
wait
echo DONE

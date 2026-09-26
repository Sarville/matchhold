# 01. Окружение: рамка, подложка, фоны, здания, капсулы

Перед работой прочитайте [README.md](README.md) (правила, STYLE-блоки, формат `LOG.md`). Промпт = STYLE (DAY или NIGHT) + промпт арта + TECH-хвост.

> **Актуализация (сессия 2, 2026-09-25).** Сделано иначе, чем ниже: рамка тонкая (150 px, проём 182..1865, не 144); фон в **3 слоя** (дальний, средний на уровне доски, передний), мастера land 4320×2160 и port 1440×2880, средний слой приглушённый с пустым центром, передний общий на все этапы; лунки тонкие (`socket_day_v3_2`, `socket_night_v2`); прозрачность проверять замером, запасной ключ `#FF00FF` + `tools/key_layer.py`. Полный список решений: [README.md](README.md), раздел «Актуально после сессии 2». Промпты E4 и E6 ниже описывают исходный однослойный вариант, реальные промпты слоёв в `tools/gen/`.

## 0. Как это устроено в игре (чтобы не рисовать лишнего)

Слои экрана снизу вверх. Каждый слой отдельный арт:

1. **Фон (bg)**: полноэкранная картинка, размытая (глубина резкости запечена в картинку). Меняется по этапам и по дню/ночи.
2. **Поле**: подложка (floor) → плитки (02-tiles.md) → рамка (frame). Рамка в центре пустая, плитки видны сквозь неё.
3. **Полоса мира** над полем: здания (только днём), герой, монстры (ночью). Земля полосы = верхний край рамки. Сама полоса прозрачная, фон виден сквозь неё.
4. **Передний план (fg)**: листва, камни, факелы по краям, вне фокуса. Центр прозрачный.
5. **HUD** (сердца, панели): 04-icons-and-misc.md.

### Не запекать в арт

- здания и людей на рамке (рамка сверху пустая: здания это отдельные спрайты, их прячет ночь);
- плитки, сердца, кнопки, панель заклинаний, текст;
- тени под зданиями и персонажами (их добавит игра, есть отдельный `shadow_blob`).

## 1. Список артов

| ID | Что | Кол-во | Мастер | Куда |
|---|---|---|---|---|
| E1 | `frame_day`, `frame_night`: рамка поля | 2 (×3 варианта) | 2048×2048 | `out/env/frame/` |
| E2 | `floor_day`, `floor_night`: подложка под плитками | 2 | 2048×2048 | `out/env/floor/` |
| E3 | `socket_day`, `socket_night`: лунка под одну плитку | 2 | 512×512 | `out/env/floor/` |
| E4 | `bg_s{1..4}_{day,night}_{land,port}`: фоны по этапам | 16 | land 3840×2160, port 1440×3120 | `out/env/bg/` |
| E5 | `bg_dragon_{land,port}`: фон боя с драконом | 2 | как E4 | `out/env/bg/` |
| E6 | `fg_{day,night}_{land,port}`: передний план | 4 | как E4, прозрачный | `out/env/fg/` |
| E7 | здания: 29 стадий + 4 состояния кристалла | 33 | 768×1024, прозрачный | `out/env/buildings/` |
| E8 | капсулы стройки на 1, 2, 3 ресурса | 3 | см. п. 7 | `out/env/capsules/` |
| E9 | небо: солнце, луна, звёзды, облака, птицы, летучие мыши | ~14 | по таблице | `out/env/sky/` |
| E10 | мелочь: листья, светлячок, искра, дым, пыль, тень-пятно | ~10 | по таблице | `out/env/ambient/` |

`land` = широкий экран (десктоп, 16:9), `port` = телефон в портрете (9:19.5).

## 2. Рефы

- День: `refs/ref-day-layout.png` (композиция, рамка с лозой, дома, вид на город слева и справа, размытый передний план).
- Ночь: `refs/ref-night-layout.png` (композиция, каменная рамка, замок на скале, мост, факелы) и `refs/ref-night-tiles.png` (**гамма ночи**: холодный тёмно-синий, тёплые огни).
- Не брать: всё из `refs/rejected/` (там здания стоят на рамке, плитки глянцевые/светлые ночью).

Рефы это мокапы, взятые как **настроение и палитра**. Их композицию целиком не копируем: рамка, плитки, сердца, панели и здания рисуются отдельно.

## 3. Гейты

- 🛑 **Гейт 2.** После `frame_day`, `frame_night`, `floor_day`, `floor_night` и **одного** фона `bg_s1_day_land` + `bg_s1_night_land` остановиться. Пользователь смотрит, как рамка, подложка и фон выглядят вместе (Claude соберёт мок-композицию).
- 🛑 **Гейт 2b.** После `bg_s1_*` (все 4 файла этапа) и первых 6 зданий (по одному на линию) остановиться на проверку масштаба.

## 4. Рамка и подложка (E1–E3)

Рамка **одна композиция** в двух материалах: день это тёплое дерево с лозой, ночь это камень с той же лозой, та же геометрия, те же места лозы, тот же профиль. Они должны совпасть пиксель в пиксель по внешнему и внутреннему краям, чтобы игра делала crossfade без прыжка.

Геометрия обеих рамок (мастер 2048×2048, квадрат):

- внешний край рамки отступает от границы кадра на 32 px; внутренняя граница проёма это **идеальный квадрат**, отступ от внешнего края 144 px со всех четырёх сторон (толщина рамки одинаковая);
- проём и всё вне рамки залить ключом `#FF00FF` (или сделать прозрачным);
- верхняя балка плоская и чистая: на ней ничего не стоит и не растёт (по ней ходят персонажи);
- лоза (плющ) только на левой стороне и в двух нижних углах, немного заходит на внешний край рамки; в проём и на верхнюю балку не заходит;
- вид строго спереди, без перспективы (ортогонально), симметрично.

**Реф:** `refs/ref-day-layout.png` (день), `refs/ref-night-layout.png` (ночь: материал рамки).

### frame_day

```
[DAY] A square wooden game-board frame, seen straight from the front, flat
orthographic view, perfectly symmetrical. Thick warm chestnut-brown planks with
soft vertical wood grain, a lighter bevel on the inner edge, small dark-brass
corner brackets and rivets. The frame is a hollow square ring: uniform thickness
on all four sides, outer edge inset slightly from the canvas edge. The inside
opening is a perfect square. The top beam is completely bare and flat. A few sage
green ivy vines climb only the left side and the two bottom corners, slightly
overlapping the frame. Fill the opening and everything outside the frame with
solid #FF00FF. Matte, no gloss. No tiles, no buildings, no people, no text.
```

### frame_night

```
[NIGHT] The exact same square game-board frame as the attached day frame: identical
outline, identical thickness, identical inner opening, identical ivy placement, but
built from cool blue-grey cut stone blocks with mortar lines and worn edges, ivy
darker and slightly bluish, faint moonlit rim light on the top-left edges. Fill the
opening and everything outside the frame with solid #FF00FF. Matte, no gloss. No
tiles, no buildings, no people, no text.
```

Прикладывать к `frame_night` **готовое одобренное `frame_day`** как реф геометрии.

### floor_day / floor_night

Подложка, которая видна в проёме, когда плитки нет (падают, убраны). Сплошная текстура без сетки и без предметов: сетку 8×8 нельзя нарисовать, она не совпадёт с плитками.

```
[DAY] A flat top-down texture, seamless-feeling, warm sand-beige packed earth and
sandstone with very subtle mottling and faint fine cracks, slightly darker vignette
toward the four corners. Matte. No grid lines, no objects, no text.
```

```
[NIGHT] A flat top-down texture, deep navy-blue slate with very subtle mottling and
faint fine cracks, slightly darker vignette toward the four corners, hint of cool
moonlit sheen. Matte. No grid lines, no objects, no text.
```

Реф: `refs/ref-day-tiles.png` (цвет и зерно песочного поля), `refs/ref-night-tiles.png` (цвет тёмного поля).

### socket_day / socket_night

Мягкая лунка под плашкой, чтобы плитка «сидела» в поле. Прозрачный фон.

```
[DAY] One square recessed socket seen from the front, rounded corners (radius about
14% of the side), a soft inner shadow on the top and left inner edges and a faint
light lip on the bottom and right, in slightly darker warm sand than the floor.
Occupies the central 88% of a transparent canvas. Matte, no gloss, no icon inside.
```

`socket_night`: то же, цвет тёмно-синий, лунка чуть темнее подложки.

## 5. Фоны (E4, E5)

Все фоны делаются **широкими (`land`)** и **вертикальными (`port`)**. Один и тот же этап в обоих форматах должен показывать одну и ту же сцену (тот же замок, тот же мост), просто скомпонованную заново. Для `port` прикладывайте готовый `land` того же этапа как реф.

Общие правила композиции:

- глубина резкости: дальние горы и небо очень мягкие, средний план (город) слегка размыт, никаких резких деталей;
- **безопасная зона** под игру (там будет поле и полоса мира): `land`: центральные 40% ширины и вся высота; `port`: вертикальная полоса от 25% до 75% высоты, вся ширина. В безопасной зоне только мягкий небо/дымка/далёкие холмы, низкий контраст, без ярких пятен и светлых объектов; крупные детали (замок, мост, река, город) только по бокам (`land`) или сверху и снизу (`port`);
- небо в верхней трети светлее, к горизонту теплее (день) или глубже (ночь);
- никаких персонажей, птиц, текста, рамок.

### Этапы

Пока это предложение. Пороги уровней героя (1–26) Claude подберёт при встраивании.

| Этап | Название | День (что видно) |
|---|---|---|
| s1 | Деревня | луга и холмы, несколько домиков с соломенными и красными крышами, деревянная мельница, грунтовая дорога, лес, далёкие горы |
| s2 | Посёлок | больше домов, каменный мост через реку, небольшая каменная сторожевая башня, поля, мельница |
| s3 | Город | каменные стены и башни, плотная застройка с красными и синими крышами, река с мостом (как в правой части `ref-day-layout.png`), на холме замок вдали |
| s4 | Столица | огромный замок на скале со стягами, водопады, арочный акведук, застройка до горизонта, золотой свет |

Ночью: та же сцена, но ночь (луна, тёплые окна и факелы, синяя дымка, силуэты елей), настроение и гамма как `ref-night-layout.png` и `ref-night-tiles.png`.

### bg_s{N}_day_land

```
[DAY] Wide 16:9 background illustration for a fantasy village game, soft
depth-of-field: distant mountains and sky are very soft, the mid-ground is gently
blurred, nothing is sharp. Stage {N}: {DAY_SCENE from the table}. Composition: the
central 40% of the width is calm and low-contrast (only soft sky, haze and distant
hills, no bright spots) so a game board can sit on top; all landmarks (buildings,
bridge, river, castle) are placed in the left and right thirds. Light sky at the top,
warmer toward the horizon. No characters, no birds, no text, no frame.
```

### bg_s{N}_night_land

```
[NIGHT] Same scene as the attached day background (same landmarks in the same
places), now at night: large moon, deep indigo sky with a few stars, warm lit
windows and torches, blue mist, dark pine silhouettes. Soft depth-of-field as in the
day version. Keep the central 40% of the width calm and dark-low-contrast. No
characters, no text, no frame.
```

Реф: `bg_s{N}_day_land` (готовый) + `refs/ref-night-layout.png`.

### bg_s{N}_{day,night}_port

```
[DAY|NIGHT] Vertical 9:19.5 version of the attached background: the same scene and
landmarks, recomposed for a tall phone screen. Keep the vertical band from 25% to
75% of the height calm, low-contrast and empty (soft sky/haze/distant hills only).
Put the sky and the skyline (castle, roofs, bridge) in the top 25% and the
foreground meadow/river/riverbank in the bottom 25%. Same soft depth-of-field.
No characters, no text, no frame.
```

### bg_dragon_{land,port}

Отдельный фон боя с драконом. Не зависит от этапа.

```
[NIGHT] Wide 16:9 background for a dragon boss fight: a stormy blood-red and ash-purple
twilight sky, heavy dark clouds lit from below by distant fire, volcanic black
cliffs and a ruined stone bridge on the sides, embers in the air, a dim
burning-village glow on the horizon. Soft depth-of-field, nothing sharp. The
central 40% of the width is calm, dark and low-contrast. No dragon, no characters,
no text, no frame.
```

Для `port` тот же промпт по правилам вертикальной перекомпоновки выше.

## 6. Передний план (E6)

Прозрачный PNG на весь кадр. Только края, центр пуст. Сильно не в фокусе (боке), чтобы не отвлекал.

```
[DAY] Out-of-focus foreground framing layer on a transparent background, wide 16:9:
large blurry sage-green leaves and a leafy branch in the top-left corner, ivy and a
few small white flowers, mossy stones in the bottom-left and bottom-right corners.
Strong depth-of-field blur (bokeh), soft edges. The central 50% of the canvas is
completely transparent. No text.
```

```
[NIGHT] Out-of-focus foreground framing layer on a transparent background, wide 16:9:
dark blurry leaves top-left, stone ruins with an iron lantern and a burning torch
in the bottom corners, ferns, warm orange glow spilling softly from the torches.
Strong depth-of-field blur (bokeh). The central 50% of the canvas is completely
transparent. No text.
```

`fg_*_port`: те же по смыслу, но верх и низ кадра вместо боков; центральная вертикальная полоса 25–75% пустая.
Реф: `refs/ref-day-layout.png` / `refs/ref-night-layout.png` (левый нижний и правый нижний углы).

## 7. Здания (E7)

**Общее.** Вид спереди-сверху (три четверти), стоит на земле, **нижний край холста = линия земли**, здание по центру. Мастер 768×1024 (соотношение 3:4, это логический размер 60×80). Прозрачный фон. Без тени под зданием. Здание видно только днём. Нужен свет `DAY`.

Здание занимает ~80% ширины и ~90% высоты, остальное запас. Каждая линия это серия апгрейдов: **та же архитектурная основа, тот же ракурс, тот же материал**, следующая стадия чуть больше, богаче, ярче. Не менять цвет крыши между стадиями одной линии без причины.

**Реф:** верхняя строка домов в `refs/ref-day-layout.png` (слева направо: дом с мельницей, красная крыша, соломенная хижина, лесопилка-леса, кузница, рынок, башня). Серию делать **лентой** (все стадии линии в одном запросе на общей сетке) и потом резать, либо **цепочкой** (стадия N по референсу N−1).

Шаблон:

```
[DAY] {SUBJECT}. Front three-quarter view, standing on the ground, ground line at the
bottom edge of the canvas, centered, fills about 80% of the width and 90% of the
height, transparent background, no cast shadow on the ground. Same architecture,
camera and materials as the previous stage of this series, but {UPGRADE}.
Matte, no gloss. No people, no text.
```

### Жилая линия (на основе grain): 4 стадии

| ID | Промпт (SUBJECT, UPGRADE) |
|---|---|
| `shack_1` | small thatched-roof wooden hut, one door, tiny stone chimney |
| `house_2` | timber-framed cottage with a red tile roof, two small windows; UPGRADE: bigger, second window, flower box |
| `fort_3` | fortified timber-and-stone house with a small wooden watch platform and a pennant; UPGRADE: sturdier, palisade fence |
| `castle_4` | small stone castle keep with two round towers and a blue banner; UPGRADE: stone, crenellations, gate |

### Кирпичник (clay): 4 стадии

| ID | SUBJECT / UPGRADE |
|---|---|
| `bricklayer_1` | clay pit with a small wooden shed and a heap of raw terracotta clay |
| `bricklayer_2` | small brick kiln with a little smoke and a few stacked bricks |
| `bricklayer_3` | larger brick kiln, stacked brick pallets beside it, more smoke |
| `bricklayer_4` | brick workshop with a tall chimney, a finished brick wall segment, wheelbarrow |

### Ткач (cloth): 4 стадии

| ID | SUBJECT / UPGRADE |
|---|---|
| `weaver_1` | tiny lean-to with a simple loom and a hanging cloth |
| `weaver_2` | market stall with a red-and-cream striped awning and rolls of fabric (as in the reference) |
| `weaver_3` | weaver's house with two looms and dyed violet fabrics hanging on a line |
| `weaver_4` | grand weaver's hall, violet and gold banners, rich fabric bolts on display |

### Кузница (stone → мечи): 8 стадий

Три яруса, как уровни камня: сталь (1–3), огонь (4–6), лёд (7–8).

| ID | SUBJECT / UPGRADE |
|---|---|
| `blacksmith_1` | small stone forge with slate roof, chimney and an anvil in front (as in the reference) |
| `blacksmith_2` | UPGRADE: wider forge, second chimney, small weapon rack |
| `blacksmith_3` | UPGRADE: two-bay forge, bellows, several steel swords displayed |
| `blacksmith_4` | dark stone forge with a red-hot furnace glow at the door; same layout as stage 3 |
| `blacksmith_5` | UPGRADE: bigger, orange fire glow spilling from windows, sparks |
| `blacksmith_6` | UPGRADE: largest fire-tier forge, flaming sword sign, strong glow |
| `blacksmith_7` | frost-tier forge, pale blue stone and blue cold flame glow, icicles on the roof |
| `blacksmith_8` | UPGRADE: grand ice-steel forge, gold trim, brightest cold glow |

### Лесопилка (wood): 8 стадий

Три яруса, как уровни дерева: простое (1–3), тёмное (4–6), золочёное (7–8).

| ID | SUBJECT / UPGRADE |
|---|---|
| `sawmill_1` | small open log shed with a hand saw and a log pile |
| `sawmill_2` | UPGRADE: bigger shed, plank stack, small water wheel |
| `sawmill_3` | UPGRADE: two-bay sawmill, larger water wheel, more planks |
| `sawmill_4` | dark hardwood sawmill, same layout as stage 3, darker timber |
| `sawmill_5` | UPGRADE: larger, second floor, stacked dark planks |
| `sawmill_6` | UPGRADE: largest dark-tier sawmill, big wheel, wide plank yard |
| `sawmill_7` | golden-trimmed timber sawmill, faint magical green leaf glow, sparkling leaves |
| `sawmill_8` | UPGRADE: grand gilded sawmill, brightest glow, golden wheel |

### Башня и кристаллы (tower)

В игре на месте башни (`x=330`) сначала стоит маркер кристаллов, потом, когда собрано 4, доступна башня.

| ID | SUBJECT |
|---|---|
| `gem_1` … `gem_4` | small stone pedestal with 1, 2, 3, 4 glowing pink-magenta mana crystals (each state adds one crystal, pedestal identical) |
| `tower_1` | round stone watch tower with a slate cone roof and a blue banner with a fleur-de-lis, as on the right of the reference |

Замечание для Claude (не для агента): в оригинальном листе у башни 5 рядов, их назначение уточняется при встраивании. Генерацию это не блокирует.

### Геометрия полосы мира (расчёт, сессия 4; решение пользователя: слот 80 на всю ширину)

Единица: логический px игры (клетка 60, доска 480, десктоп). Тонкая рамка: 1 px мастера 2048 = 480/1684 = 0,285 логического px.

| Что | Значение |
|---|---|
| Проём (доска) | 480 (портрет 560, клетка 70) |
| Рамка снаружи | 565,5 (32..2015 мастера); рельс 42,8 (150 мастера); внешний край рамки непрозрачный с 33-го px мастера |
| Линия земли | верхний внешний край рамки, **42,8 выше верха проёма**. Вдоль рельса **мини-фон** глубиной 14 (земля, песчаная дорожка, трава по заднему краю, цветочки, земляная кромка спереди; `out/env/ground/ground_strip_v2`, плитка `composed/ground_tile.png`, повтор по x). Здания и капсулы стоят на дорожке, ступни на 5,6 выше переднего края. Каменного уступа нет (смотрелся инородно на деревянной рамке) |
| Слоты | 6 на всю ширину мира 480: **жилой слот 100** (павильон-хранилище растянут по горизонтали ×1,25, качество не пострадало: исходник ~700 px на 100 логических = 300 px на ×3) и **5 слотов с шагом 76** (холст спрайта 80, здание внутри ≤ 92%, зазор между зданиями ≥ 2). `position` в коде это ЦЕНТР здания (`translateX(pos − width/2)`): жилая линия **50**, bricklayer **138**, weaver **214**, blacksmith **290**, sawmill **366**, tower и gem **442** (было 30, 90, …, 330) |
| Здание | холст 80×106,7 (3:4, мастер 768×1024, ×9,6); жилая линия 100×106,7 (мастер 960×1024); здание ≤ 92% ширины и ≤ 96% высоты, низ = земля; лист `sheets/buildings{,@2x,@3x}.png` ячейка 100×107 (жилые строки на всю ширину, остальные 80×107 у левого края, в CSS `width: 80`) |
| Капсула | **объёмная каменная плита** (верхняя плоскость нарисована в арте): 76×19 / 29 / 39 (1/2/3 ресурса, шаг сегмента ~10), верхняя плоскость 4,9; исходник `capsule_block3_v2`, 1 и 2 сегмента режутся из него `tools/build_capsules.py`; лунка 7,8, жёлоб ~52×6; прямоугольники и `stand` в `out/env/capsules/capsules.json` |
| Подъём предшественника | здание стоит на верхней плоскости капсулы (низ на `stand` 3,9 от её заднего края, 80% глубины). Высота стека: 106,7 + 39 − 2 + 6 ≈ 150 |
| Полоса мира | **150** (было 110); над проёмом 42,8 + 150 = 193 (сейчас 112): `.gameBoard margin-top` → 193, `.world height` → 150, `.world top` → −193, ниже проёма рельс ещё 42,8 |
| Хранилище | жилая линия = **павильон-хранилище**: слева высокий открытый павильон (длинной стороной к зрителю, три передние стойки, глубокий пол), справа небольшой дом/башни. Ячейки запаса **стоят на полу в проёмах между стойками, не поверх колонн** (2.5D): шаг 8,5 (ячейка 7,5 + зазор 1), вместимость по стадиям 9, 12, 16, 20 (3×3, 3×4, 4×4 и 4×4 + столбец из 4 ячеек в левом проёме), координаты каждой ячейки в `store-layout.json` (логические px кадра спрайта 100×106,7), проверка `tools/store_layout.py` → `out/env/buildings/mock_store_layout.png`. Порядок заполнения: индекс в списке, основной проём снизу вверх слева направо, у последней стадии затем левый проём. Заливка ячейки только цветом ресурса. Стадии 3–4 растянуты по вертикали ×1,23, чтобы проём под балкой был не ниже, чем у стадии 2 (~34) |
| Иконки капсулы | десктоп: иконка тайла в лунке; телефон: вместо иконки лунка заливается цветом ресурса (крошечная иконка не читается) |

Масштаб на экране: десктоп ×1,32 (здание 106×141, капсула 100 px шириной); портрет ≈ ×0,65 (слот 52 px).

Жилая линия теперь **павильон-хранилище** (см. строку «Хранилище»): под высоким открытым павильоном игра рисует запас, павильон растёт вместе с сеткой запаса (посты выше на каждой стадии), рядом дом, который к последней стадии становится замком.
Башня магии: витиеватая остроконечная (spire, полумесяц, парящие кристаллы маны), не сторожевая башня.

### Координаты для кода (пересчёт под слоты 100 + 5×76, сессия 4)

Все координаты в логических px мира (0 = левый край проёма, ширина мира 480, y вверх от линии земли, если не сказано иное). В коде менять при встраивании:

| Что | Было | Стало |
|---|---|---|
| `position` (центр) жилой линии `shack`/`house`/`fort`/`castle` | 30 | **50** (ширина 100) |
| `position` bricklayer1–4 / weaver1–4 / blacksmith1–8 / sawmill1–8 | 90 / 150 / 210 / 270 | **138 / 214 / 290 / 366** (ширина 80) |
| `position` Tower и `gem` (`world.js: gem.p(Tower.position)`) | 330 | **442** |
| `dudeSpot` (`Building.prototype.dudeSpot`) | `p + width/2` | **`p + 30`** (константа; иначе у башни было бы 442+40 = 482 за краем мира, а у жилой линии 100 = на стыке слотов). Итого героя ведёт в 80 / 168 / 244 / 320 / 396 / 472 (правее двери, как раньше) |
| Звёздочка приоритета `star.p(position)` | центр | центр, без изменений |
| Хранилище (ячейки) | `.resources` left 14, bottom 3, сетка блоков 10×10 | ячейки позиционируются по `store-layout.json` (по стадии жилой линии) в кадре спрайта жилой линии, **не сеткой**: левый верх спрайта = `position − 50`, каждая ячейка 7,5×7,5 + рамка |
| `effectDest.day` ресурсов (wood/stone/clay/cloth) | [32, −20] | **[44, −72]** относительно верха проёма (центр сетки запаса: x 44 (основной проём), y от −67 на 1-й стадии до −79 на 4-й; ниже проёма мира 42,8 рельса + ступни 5,6 + высота от пола до центра ячеек); grain [−20, 10] и mana [30, 505] зависят от новой раскладки HUD, пересчитать при встраивании |
| Границы героя `moveTo` (30 … worldWidth−30) | 30…450 | без изменений |
| Спавн монстров (`−width`, `worldWidth + width`) | | без изменений; `.world` остаётся 480 с обрезкой по краям проёма |
| Столбики с табличками, торцы мини-фона | | вне `.world`, отдельным слоем в `.gameBoard` (центры на −22 и 502 от левого края проёма, основание на линии земли), чтобы не обрезались |

### Таблички по краям мира (сессия 4)

Столбики стоят на углах рамки по краям мини-фона (над угловыми пластинами, рельс шире проёма на 43 с каждой стороны), поэтому слоты зданий не задеты. **Слева «день + фаза», справа «уровень»**; арт один и тот же (столбик с подвесной доской на цепях, пластина под число), пустой: число и значок рисует игра.

| Что | Значение |
|---|---|
| Спрайт | `out/env/signs/composed/sign_{day,night}.png`, холст 44×84 логических px (×12), низ = линия мини-фона; исходники `sign_level_day_v2`, `sign_level_night_v1` (генерация `tools/gen/gen_signs1.sh`, `gen_signs2.sh`, сборка `tools/build_signs.py`) |
| Пластина под число | день 26×23, ночь 26×24; общая безопасная область `safe` = 23×19 (x 12, y 30,5): в ней текст, чтобы при кроссфейде дня и ночи он лежал на обеих пластинах; всё в `out/env/signs/signs.json` |
| Ночью | доска тёмно-синяя, бронза, у левого конца перекладины тёплый фонарь (в дневном его нет, при кроссфейде он проявляется); цвет числа ночью золотой, днём каштановый |
| Посадка | основание столбика на линии земли, центр столбика на 22 от внешнего края рамки. Мини-фон идёт **от внешнего края до внешнего края** и заканчивается **закруглёнными торцами** (спрайты `composed/ground_cap_l/r{,_night}.png`, 22×14: четверть эллипса поднимается от нижнего внешнего угла к основанию столбика), между ними повтор `ground_tile{,_night}.png` по x |
| Десктоп | слева над числом значок фазы (солнце днём, луна ночью, ~7 px), число 11 px; справа число 15 px |
| Телефон | масштаб ~0,65: **только число** (слева день, справа уровень), без значка фазы |
| Шрифт | числа рисует игра шрифтом (в арте цифр нет) |

Анимация при смене числа:
- **Число:** старое уезжает вверх и гаснет (150 мс), новое поднимается снизу с небольшим перелётом по масштабу 1,25 → 1 (250 мс).
- **Повышение уровня:** доска качается на цепях (маятник вокруг точек подвеса, ±5° с затуханием ~900 мс), на пластине блик латуни; дополнительно при желании пара золотых искр.
- **Новый день:** число прокручивается так же; значок фазы меняется кроссфейдом (солнце ↔ луна) на закате и рассвете, ночью мерцает фонарь (яркость 0,85–1,0, период ~2 с).

## 8. Капсулы ресурсов (E8)

Капсула = замена чёрных полосок над зданием, которые показывают, сколько ресурсов уже вложено в стройку (клик по ней открывает стройку). Рисуем **только пустую раму**. Заливку (цвет ресурса) и иконку ресурса игра дорисует сама: заливка градиентом палитры класса, иконка это уменьшенная иконка тайла.

Три варианта по числу типов ресурсов в цене: 1, 2 или 3 сегмента. Логический размер 56×14 / 56×22 / 56×30, мастер ×20: **1120×280, 1120×440, 1120×600**. Один сегмент: слева круглая лунка под иконку, справа длинный пустой жёлоб (пилюля). Дневной набор (ночью капсулы скрыты).

```
[DAY] A horizontal resource progress capsule frame, {N} stacked segment(s), seen
straight from the front. Each segment: a round empty socket on the left (for an icon)
and a long empty rounded trough to the right, dark warm inset interior, framed in warm
chestnut wood with a thin brass rim and tiny brass rivets. Empty inside: no fill, no
icon, no text. Slight cast shadow inside the trough top. Matte, no gloss. Transparent
background, canvas exactly {W}x{H}.
```

Реф: рамки сердец в `refs/ref-day-layout.png` (дерево + латунь), для стиля деталей.

Хранилище (кубики 8×8 с заливкой по ширине, до 30 единиц): отдельный арт **не генерируем**. Токен ресурса берётся из готовой иконки тайла (02-tiles.md), заливка это маска. Claude сделает скриптом.

## 9. Небо и мелочь (E9, E10)

Мелкие спрайты, прозрачный фон, мастер по таблице. Свет `DAY` для дневных, `NIGHT` для ночных.

| ID | Что | Мастер | Промпт |
|---|---|---|---|
| `sun` | солнце | 512×512 | soft warm glowing sun disc with a gentle halo, no rays, no face |
| `moon` | луна | 512×512 | large pale full moon with subtle craters and a soft blue-white halo, as in ref-night-layout |
| `star_1..3` | звёзды | 128×128 | small soft four-point twinkling star, 3 slightly different sizes |
| `cloud_1..4` | облака (день) | 512×256 | fluffy soft matte cumulus cloud, warm white with pale blue shading, 4 different shapes |
| `wisp_1..2` | ночные облака | 512×256 | thin dark-blue night cloud streaks lit faintly from the moon |
| `birds_day` | стая птиц | 256×128 | three small distant birds in flight, simple soft silhouettes |
| `bats_night` | летучие мыши | 256×128 | three small bats in flight, dark silhouettes, wings spread |
| `leaf_1..3` | падающий лист | 128×128 | one small green leaf, 3 shapes, soft matte |
| `firefly` | светлячок | 64×64 | one tiny warm yellow-green glowing dot with soft glow |
| `ember` | искра/уголёк | 64×64 | one tiny orange glowing ember with a soft glow |
| `dust` | пылинка | 64×64 | one soft round dust mote, pale, faint |
| `smoke_1..2` | клуб дыма | 256×256 | soft grey-white puff of smoke, matte, two shapes |
| `shadow_blob` | тень-пятно под ногами | 256×128 | soft dark elliptical contact shadow, semi-transparent, blurred edges, no hard edge |

Реф: настроение `refs/ref-day-layout.png` (облака, листья), `refs/ref-night-layout.png` (луна, летучие мыши).

## 10. Порядок

1. E1 → E3 (рамка, подложка, лунки), 🛑 Гейт 2.
2. E4 этап s1 (день и ночь, land; port), E5 (дракон), E6 (передний план), 🛑 Гейт 2b вместе с первыми зданиями.
3. Здания остальных линий и стадий.
4. Капсулы, небо, мелочь.
5. Этапы s2–s4 фонов.

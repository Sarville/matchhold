# 02. Тайлы: плашка + иконка ресурса

Перед работой прочитайте [README.md](README.md). Промпт = STYLE (DAY или NIGHT) + промпт арта + TECH-хвост.

## 0. Идея

Плитка **собирается из двух независимых артов**: пустая плашка (одна для дня, одна для ночи) и иконка ресурса на прозрачном фоне. Так плашка одинакова у всех 65 граней, иконки можно перерисовывать независимо, а стиль держится проще. Склейка делается скриптом (Claude), не генератором.

- День: тёплая светлая матовая плашка цвета `ref-day-tiles.png`. Никакого глянца.
- Ночь: тёмно-синяя плашка и гамма `ref-night-tiles.png`, иконки светлее плашки и с мягким glow.

## 1. Рефы

| Реф | Для чего |
|---|---|
| `refs/ref-day-tiles.png` | эталон дня: цвет плашки, матовость, форма иконок (сноп, камень, брёвна, ткань) |
| `refs/ref-night-tiles.png` | эталон ночи: цвет плашки, свечение, форма иконок (меч, щит, паутина, замок, арка) |
| `refs/ref-day-layout.png`, `refs/ref-night-layout.png` | общая гамма |
| `refs/rejected/*` | глянцевые плитки: так не делать |

## 2. Как плитки устроены в игре (справка для Claude при сборке)

- Логическая клетка 60×60 (десктоп) / 70×70 (портрет), грань внутри 52×52 (`.daySide`, `.nightSide`). В портрете грань растягивается через `scale(1.15)` (~60 px). Ночью тайл переворачивается (`rotateY(180deg)`): день и ночь это две разные картинки.
- Лист `tiles.png` 312×988 = 6 колонок × 19 рядов по 52 px.

| Колонка | Класс | Уровней | Ряды дня | Ряды ночи |
|---|---|---|---|---|
| 0 | grain | 4 | 0–3 | 9–12 |
| 1 | stone | 9 | 0–8 | 9–17 |
| 2 | wood | 9 | 0–8 | 9–17 |
| 3 | clay | 4 | 0–3 | 9–12 |
| 4 | cloth | 4 | 0–3 | 9–12 |
| 5 | mana | 1 | 0 | 9 |

- Ряд 18: боевые грани дракона (grain/clay/cloth). Они подменяют ночную грань.
- Уровень тайла растёт вместе со зданием. Матч определяется классом, уровень влияет только на картинку.
- Ночные грани это не «ночная версия предмета», а смысловой переворот: stone → меч, wood → щит, остальные → маркер монстра (`nightEffect`).
- **Итого граней: 65** (день 31, ночь 31, дракон 3).
- Известные огрехи оригинала, чинит Claude при встраивании: ночной блок в CSS с `-467px`, а в `sprites.js` с 468 (верно 468); правила `.wood7 .tile.wood > div` и `.clay3 .tile.clay > div` задают ночную позицию обеим граням.

## 3. Порядок и гейты

1. **T0.** Плашки `plate_day`, `plate_night` (3 варианта каждой).
2. **T1.** Якорные дневные иконки: по одной на каждый из 6 классов (уровень 1) + `ref-day-tiles.png` как реф.
3. 🛑 **Гейт 1.** Claude соберёт 6 плиток на плашках и покажет пользователю. Пользователь утверждает: плашку, стиль иконок, **фиолетовую ткань** (см. README, палитра), четкость классов. Дальше не генерировать.
4. **T2.** Дневные серии (по классам).
5. **T3.** Ночные якоря (по одному на класс) → 🛑 **Гейт 1b** (утвердить ночь), затем ночные серии.
6. **T4.** Три грани дракона.
7. **T5.** Claude: сборка, проверка, экспорт листов.

## 4. Плашки (T0)

Один квадрат на прозрачном фоне, мастер 512×512, плашка занимает центральные 88% (остальное запас под мягкую тень). Иконки внутри нет.

### plate_day

```
[DAY] One square game tile plate, seen straight from the front, slightly raised like
a soft stone-and-clay tile, rounded corners (radius about 14% of the side). Warm
cream-beige face (#EFE3CC) with a very soft matte gradient, a subtle lighter bevel
along the top and left edges, a slightly darker warm-beige edge along the bottom and
right, a thin outline a little darker than the face, a faint soft contact shadow just
outside the bottom-right. No icon, no pattern, no text, no gloss. Occupies the central
88% of a transparent square canvas.
```

Реф: `refs/ref-day-tiles.png`. Плашка должна выглядеть как плитки на этом рефе: светлые, тёплые, матовые, с мягким объёмом.

### plate_night

```
[NIGHT] One square game tile plate, seen straight from the front, slightly raised,
rounded corners (radius about 14% of the side), same shape, same proportions and same
bevel as the attached day plate but deep navy-slate (#2E3853) with a very soft matte
gradient, a faint cool moonlit rim light along the top and left edges, a darker
navy edge along the bottom and right, a thin outline a little darker than the face,
a faint soft contact shadow just outside the bottom-right. No icon, no pattern, no
text, no gloss. Occupies the central 88% of a transparent square canvas.
```

Реф: готовая одобренная `plate_day` (форма) + `refs/ref-night-tiles.png` (цвет).

### select_ring_day / select_ring_night

Кольцо выбора плитки вместо `select-border.png`. Мастер 512×512, центр прозрачный.

```
[DAY|NIGHT] A square selection ring for a game tile: rounded-square outline slightly
larger than the tile plate (outer edge at 96% of the canvas), soft {warm gold |
cool pale blue} glowing line about 4% thick with a gentle outer glow, fully transparent
inside and outside. No fill, no text.
```

## 5. Иконки: общие правила

- Мастер **512×512**, прозрачный фон, один предмет по центру, занимает не более **340×340** (запас на glow и сборку).
- Ракурс три четверти сверху, лёгкая тень внутри самого предмета, **без тени на землю и без плашки** (плашку и тень добавляет скрипт).
- Толщина контура, свет и уровень детализации **одинаковы у всех иконок**.
- **Семейство серии.** Уровни одного класса это один предмет-семья: тот же ракурс, та же толщина контура. Следующий уровень богаче и ярче.
- **Силуэт класса** должен читаться в оттенках серого на 52 px:
  - grain: вертикальный сужающийся пучок/еда;
  - wood: диагональные брёвна и доски;
  - stone: гранёная массивная глыба или слитки;
  - clay: кирпичи в ряд/стопкой с видимым швом, красно-терракотовые;
  - cloth: мягкие складки и рулоны, **фиолетовые**, с округлыми линиями (чтобы не путать с кирпичом);
  - mana: капля-кристалл с искрами.
- Цвета классов см. README (палитра).

### Шаблон для одной иконки

```
{STYLE}. A single game tile icon: {SUBJECT}. Three-quarter view from above, centered,
fills about 66% of the canvas, transparent background, no ground shadow, no plate, no
frame, no text. Class palette: {PALETTE}. Readable at 52 px.
```

### Шаблон ленты (серия за один запрос)

Лента делается **не более чем на 3–5 иконок**: 9-уровневые серии режьте на 3 запроса по 3.

```
{STYLE}. A horizontal strip of {N} game tile icons on a flat solid #FF00FF
background, each icon centered in its own equal square cell with clear space
between cells, same size, same camera angle, same outline weight, same palette
family. Each icon is a strict upgrade of the previous one: the same kind of object,
richer, more ornate and more valuable, from left to right. Tiers: 1) {…} 2) {…} 3) {…}.
Class palette: {PALETTE}. No plate, no shadow, no text.
```

### Шаблон цепочки (если лента расползается)

```
Using the attached icon as the reference, draw the next tier of the same series.
Keep the same camera angle, outline weight, palette family and lighting.
Make it clearly an upgrade: {WHAT TO ADD}. Transparent background, no plate.
```

Реф: предыдущий уровень + `refs/ref-day-tiles.png`.

## 6. Якорные дневные иконки (T1)

Шесть штук, по классу. Три варианта каждой. Цель: утвердить стиль на Гейте 1.

| ID | SUBJECT | PALETTE |
|---|---|---|
| `grain_1` | a golden wheat sheaf tied with a rope, plump grains, as in the reference | honey gold |
| `wood_1` | two stacked chestnut logs with visible round ends and rings, as in the reference | chestnut brown |
| `stone_1` | a rough faceted grey stone block, cool grey with lighter top facets, as in the reference | cool grey |
| `clay_1` | a rough lump of raw terracotta clay with a couple of finger marks | terracotta red |
| `cloth_1` | a soft loose bundle of violet thread/cotton fibre with light cream highlights | violet |
| `mana_1` | a glowing pink-magenta teardrop mana crystal with small sparks | magenta-pink |

## 7. Дневные иконки: полный список (31)

Все с шаблоном из п. 5 и STYLE `DAY`. Реф каждого: одобренные якоря (п. 6) того же класса + `refs/ref-day-tiles.png`.

Файл: `out/tiles/icons-day/<класс>_<уровень>_v<N>.png`.

### grain (4): золото, еда

| ID | SUBJECT |
|---|---|
| `grain_1` | wheat sheaf (якорь) |
| `grain_2` | a fuller, bound wheat sheaf with a bow and more grains, richer gold |
| `grain_3` | a roasted chicken leg on the bone, golden-brown glaze |
| `grain_4` | a glazed ham on the bone with herbs, the richest food |

### stone (9): три яруса по три, серый → тёмный → голубой

| ID | SUBJECT |
|---|---|
| `stone_1` | rough grey boulder (якорь) |
| `stone_2` | a cut grey stone ingot |
| `stone_3` | a stack of three grey ingots |
| `stone_4` | an ember rock with glowing orange lava cracks |
| `stone_5` | a dark obsidian ingot with red veins |
| `stone_6` | a stack of three dark obsidian ingots |
| `stone_7` | a pale blue icy crystal shard |
| `stone_8` | a blue steel ingot with a cold glow |
| `stone_9` | a stack of blue ingots with the brightest cold glow |

### wood (9): дерево → тёмное → золочёное

Отклонение от оригинала (было золотые слитки на 8–9): золочёное дерево, чтобы колонка не путалась со stone.

| ID | SUBJECT |
|---|---|
| `wood_1` | two chestnut logs (якорь) |
| `wood_2` | a smooth plank |
| `wood_3` | a stack of three planks |
| `wood_4` | a dark hardwood log |
| `wood_5` | a dark plank |
| `wood_6` | a stack of dark planks |
| `wood_7` | a magic branch with shimmering green leaves |
| `wood_8` | a plank with a gold rim |
| `wood_9` | a stack of gilded planks with a soft glow |

### clay (4): терракота

| ID | SUBJECT |
|---|---|
| `clay_1` | raw clay lump (якорь) |
| `clay_2` | one baked red brick |
| `clay_3` | a neat stack of three bricks with visible mortar edges |
| `clay_4` | a piece of brick wall topped with a small tower crenellation |

### cloth (4): фиолетовый, от полотен к рулонам

Решение пользователя (сессия 3): клубок нити не читался как ткань. Начинаем со сложенных полотен, богаче уровни идут рулонами.

| ID | SUBJECT |
|---|---|
| `cloth_1` | a neatly folded violet piece of cloth with a light lavender stripe (якорь) |
| `cloth_2` | a stack of two or three folded violet cloths |
| `cloth_3` | a neat violet cloth roll (bolt) tied with a cream ribbon |
| `cloth_4` | two royal violet cloth rolls with a pattern and gold trim |

### mana (1)

| ID | SUBJECT |
|---|---|
| `mana_1` | glowing magenta mana crystal (якорь) |

## 8. Ночные иконки: полный список (31)

STYLE `NIGHT`. Иконки светлее плашки, с мягким **glow цвета класса** (grain зелёный, clay оранжево-красный, cloth фиолетовый, mana пурпурный, sword стально-голубой, shield тёплый золотисто-коричневый). Один предмет-эмблема по центру, не сцена.

Реф: соответствующая **дневная иконка того же класса и уровня** (цвет и семейство) + `refs/ref-night-tiles.png` (гамма и свечение). Иконки на `ref-night-tiles.png` (меч, щит, паутина, замок, арка) это референс стиля, не финальный список.

Файл: `out/tiles/icons-night/<класс>_<уровень>_v<N>.png`. Монстры соответствуют `nightEffect` в `gamecontent.js`: уровень 1 это `default`, уровни 2–4 это здания по возрастанию.

### grain → земля и нежить (4), зелёный glow

| ID | Монстр | SUBJECT |
|---|---|---|
| `grain_1` | zombie | a small mossy gravestone with a hand reaching from the earth, green mist |
| `grain_2` | hauntedArmour | an empty knight helmet on a stand with glowing green eyes |
| `grain_3` | earthElemental | a mossy stone golem head with a green glow |
| `grain_4` | demon | a horned demonic eye with **green** flame (не красно-оранжевый — сливался с огненными мечами stone, решение сессии 7) |

### clay → мелкие и водные (4), оранжевый glow (для waterElemental и imp голубой)

| ID | Монстр | SUBJECT |
|---|---|---|
| `clay_1` | rat | a rat hole with two glowing red eyes |
| `clay_2` | spider | a spider on a web, **rust-red** (не оранжево-терракотовый, решение сессии 7) |
| `clay_3` | waterElemental | a water drop with a face, blue glow |
| `clay_4` | imp | a **faceted hexagonal** flask of **blue** potion with a tiny imp inside (не округлая зелёная — сливалась с grain, решение сессии 7) |

### cloth → нежить и огонь (4), фиолетовый glow

| ID | Монстр | SUBJECT |
|---|---|---|
| `cloth_1` | skeleton | a skull with crossed bones, dim violet glow |
| `cloth_2` | lizardman | a swamp vine and a scaly lizard head, **sand/tan scales** (не зелёный — совпадал с зелёными grain-иконками, решение сессии 7) |
| `cloth_3` | fireElemental | a flame with a face, orange glow |
| `cloth_4` | warlock | a dark portal with golden horns and violet magic |

### mana → лич (1), пурпурный glow

| ID | Монстр | SUBJECT |
|---|---|---|
| `mana_1` | lich | a crystal skull with a red glow |

### stone → мечи (9), стально-голубой glow

Три яруса по три: сталь, огонь, лёд. Меч по диагонали, остриё вверх-вправо, как на `ref-night-tiles.png`.

| ID | SUBJECT |
|---|---|
| `stone_1` | a simple steel sword |
| `stone_2` | a steel sword with a crossguard |
| `stone_3` | a polished steel sword with an ornate hilt |
| `stone_4` | a dark steel blade with a red flame along it |
| `stone_5` | a dark blade with brighter fire |
| `stone_6` | a dark blade wrapped in strong fire |
| `stone_7` | an icy blue blade with a cold glow and a golden hilt |
| `stone_8` | a brighter icy blade with a golden hilt |
| `stone_9` | an icy blade with a golden hilt and a halo |

### wood → щиты (9), тёплый золотисто-коричневый glow

Круглый щит, вид спереди, как на `ref-night-tiles.png`.

| ID | SUBJECT |
|---|---|
| `wood_1` | a round plain wooden shield with a metal boss |
| `wood_2` | a wooden shield with rivets |
| `wood_3` | a wooden shield with an iron rim and an emblem |
| `wood_4` | a dark iron kite shield |
| `wood_5` | a dark iron kite shield with a central spike |
| `wood_6` | a dark iron kite shield with a coat of arms |
| `wood_7` | a gilded shield with faint glowing runes |
| `wood_8` | a gilded shield with brighter runes |
| `wood_9` | a gilded shield with brightest runes and a halo |

## 9. Грани боя с драконом (3)

Подменяют ночную грань во время боя. STYLE `NIGHT`, драматичнее, glow сильнее. Реф: ночные иконки того же класса.

| ID | Класс | Эффект | SUBJECT |
|---|---|---|---|
| `dragon_grain` | grain | WingBuffet | a swirling gust of wind carrying a green leaf, green glow |
| `dragon_clay` | clay | IceBeam | a sharp icy blue crystal with frost, cold glow |
| `dragon_cloth` | cloth | FireBlast | a bright roaring flame, orange-yellow glow |

Файл: `out/tiles/icons-dragon/dragon_<класс>_v<N>.png`.

## 10. Сборка (делает Claude, не генератор)

1. Вырезать фон, обрезать по предмету, центрировать, привести к одному масштабу с полем.
2. `плитка = плашка + иконка`: иконка по центру плашки (чуть выше центра на 2%), падающая тень иконки лёгкая, ночью glow цвета класса. Готовая грань: `out/tiles/composed/day_<класс>_<уровень>.png`, `night_…`, `dragon_…`.
3. Манифест `rebranding/tiles-manifest.json`: файл → колонка, ряд, блок (`day`/`night`/`dragon`). Скрипт (Pillow) кладёт грани в лист шагом 52 × масштаб и выдаёт `tiles@2x.png` (624×1976) и `tiles@3x.png` (936×2964). Логические координаты в CSS не меняются, только `background-size: 312px 988px` и media-запрос по `min-resolution`. Если грань в портрете (~60 px при DPR 3) окажется мягкой, добавить `@4x`.
4. Проверка: все 65 граней в реальных 52 px (и в 60 px), в оттенках серого (6 классов различимы), рядом по 6 классов, день на `floor_day`, ночь на `floor_night`.
5. Встраивание в `www/img/`, правка CSS (рамка/фон плитки теперь в картинке, CSS-рамку и белый/чёрный `.tileContainer` убрать), пересборка `deploy`.

## 11. Чек-лист для агента

- [ ] `plate_day` ×3, `plate_night` ×3
- [ ] `select_ring_day`, `select_ring_night`
- [ ] 6 якорей (п. 6), стоп на Гейте 1
- [ ] дневные иконки 31
- [ ] ночные якоря (по классу), стоп на Гейте 1b, затем ночные иконки 31
- [ ] грани дракона 3
- [ ] все записаны в `out/LOG.md`

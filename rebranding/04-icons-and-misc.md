# 04. Иконки, HUD и вспомогательные арты

Перед работой прочитайте [README.md](README.md). Промпт = STYLE (DAY или NIGHT) + промпт арта + TECH-хвост.

## 0. Что здесь

Всё, что в игре стоит поверх поля и вокруг него: сердца, панели, лут, заклинания, снаряды, эффекты, знак и лого. Плитки в 02, окружение в 01, персонажи в 03.

## 1. Рефы

- `refs/ref-day-layout.png`: сердца (каждое в деревянном кольце с листиком), стиль дерева и латуни.
- `refs/ref-night-layout.png`: нижняя правая панель с тремя круглыми слотами в золотых кольцах (синее зелье, стрела/предмет, красное зелье), сердца, каменные детали.
- `refs/ref-night-tiles.png`: меч, щит и стиль иконок ночью (те же меч и щит в HUD).

## 2. Гейты

- 🛑 **Гейт 4.** После `heart_socket_day`, `heart_fill`, `slot_ring_day`, `slot_ring_night`, `loot_health_potion`, `loot_mana_potion`. Пользователь утверждает стиль HUD. Дальше не генерировать.

## 3. Шаблон иконки

Мастер по таблице, прозрачный фон, один предмет по центру, занимает около 66% холста, вид спереди или три четверти, **без тени на землю**, без плашки и текста.

```
{STYLE}. A single game HUD icon: {SUBJECT}. Centered, fills about 66% of the canvas,
transparent background, no ground shadow, no text. Matte hand-painted 3D look.
```

Не переставлять свет: сверху-слева.

## 4. HUD-набор

Обе версии (`_day` и `_night`) одной геометрии, отличаются материалом: день это тёплое дерево и латунь, ночь это тёмный камень и железо с тёплым свечением.

| ID | Что | Мастер | SUBJECT |
|---|---|---|---|
| `heart_socket_day` / `_night` | пустое сердце в кольце | 512×512 | round ring holding an EMPTY heart: {warm chestnut wood ring with brass rim and a small leaf on the left \| dark stone ring with iron rim}; inside the ring a pale, empty, slightly recessed heart-shaped hollow (cream in day, dark slate in night) |
| `heart_fill` | красное сердце (заливка) | 512×512 | a plump red heart exactly the shape and size of the empty heart hollow, soft matte, no ring. **Совпадает по форме и положению с пустым сердцем в `heart_socket`** (игра обрезает его по ширине, поэтому полное сердце должно лечь на пустое) |
| `heartbig_socket_day` / `_night` | пустое золотое сердце (бонусное) | 512×512 | same as `heart_socket` but the ring is gold and slightly larger |
| `heartbig_fill` | золотое сердце | 512×512 | a plump gold heart with tiny sparkles, same registration as `heartbig_socket` |
| `slot_ring_day` / `_night` | круглый слот (инвентарь, кнопки заклинаний) | 512×512 | empty round slot: {gold ring with tiny gold beads at the bottom, as in the reference \| stone ring with iron studs and beads}; empty dark inset centre |
| `inventory_plank_day` / `_night` | панель с 3 слотами (нижний правый угол) | 1536×512 | a horizontal plank plate that holds three round slots, {wood and brass \| stone and iron}, with three empty round hollows evenly spaced; hollows empty |
| `bar_frame_day` / `_night` | рамка полосы (опыт, здоровье босса) | 1536×512 | horizontal empty trough frame {wood with brass rims \| stone with iron rims}, rounded ends, dark empty inset; no fill, no icon, no text. Claude режет на 9 частей, растягивает и поворачивает (полоса опыта в игре вертикальная) |

Промпты для пар `_day` / `_night`: STYLE соответственно `DAY` и `NIGHT`. Реф для `_night`: одобренный `_day` (геометрия).

## 5. Лут и предметы

Всё STYLE `DAY` (предметы лежат в слотах, кольцо даёт день/ночь). Мастер 512×512. Свет сверху-слева.

| ID | Что в игре | SUBJECT |
|---|---|---|
| `loot_health_potion` | лечит половину здоровья | a round-bottom glass flask with a cork, filled with glowing red liquid, tiny bubbles (как красное зелье в референсе) |
| `loot_mana_potion` | даёт половину маны | a round-bottom glass flask with a cork, filled with glowing blue liquid, tiny bubbles (как синее зелье в референсе) |
| `loot_bomb` | урон всем монстрам | a round black iron bomb with a lit fuse and a small spark |
| `loot_equipment` | пополняет меч и щит | a small whetstone and a hammer crossed over a tiny shield (repair kit) |
| `loot_shard` | осколок маны | a single glowing magenta mana crystal shard with sparkles |
| `loot_dragon_scroll` | вызывает дракона (особый лут) | a rolled parchment scroll with a red wax seal bearing a small dragon emblem, faint red glow |
| `chest_closed` | сундук | a small wooden treasure chest with brass fittings, lid closed, seen from the front |
| `chest_open` | сундук после подбора | the same chest with the lid open, empty inside with a faint warm glow |

`chest_open`: реф = готовый `chest_closed`, та же геометрия.

## 6. Заклинания и состояния

Четыре заклинания и три состояния. STYLE `DAY`, цветные, ставятся в `slot_ring_*`. Мастер 512×512.

| ID | Что в игре | SUBJECT |
|---|---|---|
| `spell_reset_board` | перемешать поле | two curved arrows chasing each other in a circle around a tiny tile, warm gold |
| `spell_haste` | ускорение героя | a small winged boot, light blue speed swooshes |
| `spell_freeze_time` | заморозить время | a pocket stopwatch covered in ice crystals, pale blue |
| `spell_phase_change` | сменить день/ночь | a sun and a crescent moon overlapping, warm gold and cool blue |
| `state_haste` | активное состояние | same as `spell_haste`, simpler, bolder |
| `state_freeze_time` | активное состояние | same as `spell_freeze_time`, simpler, bolder |
| `state_frozen` | герой заморожен драконом (урон в 2 раза меньше) | a blue ice crystal cluster |

## 7. Снаряды и эффекты

Прозрачный фон. Снаряды рисуются **горизонтально, летят вправо**, нос справа (игра сама поворачивает влево). Кадры анимации, если сказано, идут в одну полосу слева направо на ключе (правила ключа см. README).

| ID | Что | Мастер | SUBJECT |
|---|---|---|---|
| `proj_arrow` | стрела (skeleton, lizardman) | 512×128 | a wooden arrow with grey feathers and a steel tip, pointing right, horizontal |
| `proj_fireball` | огненный шар (fireElemental, warlock, дракон) | 512×256 | a small blazing fireball with a short trailing flame behind it, flying right, orange and yellow |
| `fx_ice_block` | ледяной блок вокруг героя при заморозке | 512×512 | a translucent pale-blue block of ice, slight frost highlights, empty inside, seen from the front |
| `fx_ice_beam` | ледяной луч дракона (4 кадра) | 4×(512×256) | a beam of ice shards and frost mist flying right, bright pale blue and white, each frame different |
| `fx_fire_blast` | огненный вал дракона (4 кадра) | 4×(512×256) | a roaring blast of flame flying right, orange, yellow and red, each frame different |
| `fx_wing_gust` | порыв крыльев дракона | 512×512 | a big swirl of wind with flying green leaves and dust, pale green-white |
| `fx_hit_spark` | искра при попадании | 256×256 | a small star-shaped hit spark, warm white and yellow, with tiny sparks |
| `fx_slash` | дуга меча | 512×256 | a curved white sword-slash arc with a soft glow, swipe from upper left to lower right |
| `fx_level_up` | вспышка при новом уровне | 512×512 | a ring of golden light with rising sparkles and stars, transparent centre |
| `fx_explosion_1..4` | взрыв бомбы (4 кадра) | 4×(512×512) | a cartoon puff explosion growing then fading: 1 small bright flash, 2 big orange fireball, 3 fireball with smoke, 4 dissipating smoke |
| `fx_heal` | лечение | 512×512 | a soft green glow with rising plus-shaped sparkles |

## 8. Панели и кнопки интерфейса (фаза 2, после Гейта 4)

Меню, сохранения, статистика, выбор сложности сейчас рисуются CSS-рамкой `litBorder` (чёрная/белая). Чтобы они не выбивались из нового стиля:

| ID | Что | Мастер | SUBJECT |
|---|---|---|---|
| `panel_day` / `_night` | панель меню (растягивается 9 частями) | 1024×1024 | square panel with a thick rounded border, {warm cream parchment inside, wood border with brass corners \| dark slate inside, stone border with iron corners}, empty centre, symmetrical |
| `button_day` / `_night` | плашка кнопки | 1024×384 | horizontal rounded button plate, slightly raised, {wood and brass \| stone and iron}, no text, empty face |

## 9. Фирменный знак (без текста)

Текст в логотипе AI рисует ненадёжно, поэтому слово **MATCHHOLD** Claude набирает шрифтом. Здесь только эмблема.

| ID | Что | Мастер | SUBJECT |
|---|---|---|---|
| `logo_emblem` | эмблема на титул и в меню | 1024×1024 | a heraldic emblem: a small round-towered castle keep over two crossed items (a sword and a builder's hammer), a blue banner with a golden fleur-de-lis, warm gold and blue, front view, transparent background |
| `badge_icon` | значок игры (og:image, apple-touch-icon, favicon) | 1024×1024 | the same emblem placed on a rounded-square badge with a warm sand background and a wooden edge; fills the badge with safe margins; no text |

Реф: `refs/ref-day-layout.png` (флаг с геральдической лилией на башне), `refs/ref-night-layout.png` (синее знамя с лилией).

Титульный экран: фон = `bg_s1_day_land` + `fg_day_land` (01-environment.md), эмблема сверху, слово Claude.

## 10. Не генерировать (делает Claude)

- Иконки-глифы меню (меню-гамбургер, музыка, звук, галочка, крестик, экспорт, импорт, корзина): простые SVG в палитре дня и ночи. AI даёт нестабильный набор.
- Логотипы соцсетей (Twitter, Facebook, Reddit, Tumblr и др.): чужие товарные знаки, не генерируем. Оставляем оригинальные или заменяем монохромными SVG.
- Индикаторы меча и щита в HUD: это те же **ночные иконки** `stone_1..9` и `wood_1..9` (02-tiles.md) без свечения и без плашки.
- Токены хранилища (кубики) и иконки ресурсов в капсулах: уменьшенные готовые иконки тайлов.
- Цвет заливки полос и капсул: градиенты палитры класса в CSS.
- Загрузочный спиннер и курсоры: оставить как есть.

## 11. Чек-лист для агента

- [ ] Гейт 4: `heart_socket_day`, `heart_fill`, `slot_ring_day`, `slot_ring_night`, `loot_health_potion`, `loot_mana_potion` (3 варианта каждый)
- [ ] остальной HUD-набор (п. 4)
- [ ] лут и сундук (п. 5)
- [ ] заклинания и состояния (п. 6)
- [ ] снаряды и эффекты (п. 7)
- [ ] панели и кнопки (п. 8)
- [ ] эмблема и значок (п. 9)
- [ ] все записаны в `out/LOG.md`

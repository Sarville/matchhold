# 03. Анимация персонажей: герой, монстры, дракон

Перед работой прочитайте [README.md](README.md). Промпт = STYLE (DAY для героя, NIGHT для монстров) + промпт арта + TECH-хвост.

## 0. Подход

Цельная 2D покадровая анимация. **Один референс-лист персонажа → полосы кадров по каждому действию → Claude собирает спрайт-лист.** Никаких разрезных частей (кроме дракона: голова и шея у него уже отдельные детали).

Кадры в игре показываются раз в 100–300 мс (3–10 к/с). Поэтому 4 кадра это **4 чётко разных ключевых позы**, а не микродвижения: разница между соседними кадрами должна быть заметна на 40 px.

## 1. Рефы

- Внешний вид монстров: ночные иконки `out/tiles/icons-night/*` (когда одобрены) и таблица в п. 5. Сами иконки это эмблемы, а не персонажи. Для дизайна персонажа берите описание в таблице.
- Гамма, свет, матовость: `refs/ref-night-layout.png` (герой в синем капюшоне и монстры на верху рамки: гоблин, скелет, слайм), `refs/ref-day-layout.png` (жители на верху).
- Оригинальные спрайты (для справки по позам, они одноцветные): `www/img/monsters.png`, `www/img/dragonsprite.png`.

## 2. Правила для всех полос кадров

1. **Все персонажи смотрят вправо** (кроме дракона: он смотрит влево, см. п. 6). Левые ряды Claude получает зеркалом, отдельно левые не рисовать.
2. Одна полоса = одно действие = **4 кадра слева направо**, равные ячейки, на сплошном ключе `#FF00FF` (см. README). Без сетки, номеров, линий-направляющих.
3. **Один персонаж на всех полосах**: та же одежда, те же цвета, пропорции, толщина контура, масштаб. Всегда прикладывайте: реф-лист персонажа + кадр 0 полосы `walk` того же персонажа как эталон масштаба.
4. **Ступни на одной линии** внутри полосы (линия земли на 88% высоты ячейки), тело по центру ячейки по горизонтали (для рывков атаки допускается смещение вперёд).
5. В стойке фигура занимает около 60% высоты ячейки. Взмахи и удары могут выходить на всю ширину ячейки.
6. **Ключевой кадр действия должен быть на своём месте** (п. 4): игра наносит урон, выпускает снаряд и т. д. на конкретных кадрах.
7. Размер ячейки:

| Класс | Ячейка | Кому |
|---|---|---|
| S | 768×768 | герой, zombie, skeleton, lizardman, warlock, fireElemental, imp, rat |
| L | 1024×1024 | demon, earthElemental, hauntedArmour, spider, waterElemental, lich |

Полоса = 4 ячейки в ряд (3072×768 или 4096×1024). Если модель не даёт такой формат, **запасной вариант**: 2×2 сетка, либо по одному кадру на запрос (в каждом запросе реф-лист + предыдущий кадр этой полосы).

8. Прозрачность/ключ: как в README. Ключ, которого нет в персонаже (для zombie, lizardman используйте `#FF00FF`, для warlock/lich с пурпуром `#00FF00`).

## 3. Порядок и гейты

1. **A0.** Реф-лист героя: 3 варианта. 🛑 **Гейт 3.** Пользователь выбирает вариант.
2. **A1.** Герой: полосы из п. 4. Claude собирает, проверяет в браузере. 🛑 **Гейт 3a.** Пользователь смотрит движение.
3. **A2.** Два монстра для проверки метода: `zombie` (ближний бой) и `skeleton` (дальний). Реф-лист + полосы. 🛑 **Гейт 3b.**
4. **A3.** Остальные 12 монстров по одному (реф-лист → полосы). После каждого монстра запись в `LOG.md`.
5. **A4.** Дракон (п. 6): начинать только после того, как Claude подтвердит состав деталей (см. п. 6).

## 4. Герой

Клетка в игре 34×32 логических px (внутри рисуем крупно, Claude ужмёт). Классы: **S**.

### Дизайн

Пока предложение, утверждается на Гейте 3. Симпатичный молодой строитель-воин: 2.5-3 головы в росте, каштановая туника, кожаный пояс, **синий капюшон и шарф** (как у маленького героя на `ref-night-layout.png`), прочные сапоги, короткий меч в правой руке. Одежда и цвета одинаковы днём и ночью.

**Реф-лист героя** (`hero_ref`, 3 варианта):

```
[DAY] Character reference sheet on a flat solid #FF00FF background: a small
friendly young builder-hero, 2.5 heads tall, chestnut tunic, leather belt, blue
hood and scarf, sturdy boots, a short sword in the right hand. Three poses side by
side, all facing right: neutral standing, mid-stride walking, sword raised for a
strike. Chunky rounded shapes, matte hand-painted 3D look, same outline weight in
every pose. No text, no labels, no grid.
```

Реф: `refs/ref-night-layout.png` (герой сверху слева), `refs/ref-day-layout.png` (жители).

### Действия героя (ряды исходного листа)

Столбец «ряд» это индекс ряда в старом `monsters.png` (Claude соберёт лист в том же порядке).

| Ряд | ID полосы | Что нарисовать (4 кадра) | Ключевой кадр |
|---|---|---|---|
| 0 | `hero_idle` | стоит: дыхание, перенос веса, лёгкое покачивание плаща; цикл | нет |
| 1 (→2 зеркало) | `hero_walk` | шаг вправо: 1 опорная (правая нога вперёд), 2 проходная (тело выше), 3 опорная (левая вперёд), 4 проходная | нет |
| 3 (→4) | `hero_attack_sword` | удар мечом: 0 замах назад, **1 удар (лезвие в самой дальней точке)**, 2 инерция, 3 возврат в стойку | **кадр 1 = попадание** |
| 11 (→12) | `hero_attack_fist` | безоружный удар: 0 замах, **1 выпад кулаком**, 2 инерция, 3 возврат | **кадр 1 = попадание** |
| 5 (→6) | `hero_die` | падение: 0 удар/отшатывание, 1 оседает на колени, 2 садится, 3 лежит; **кадр 3 = конечная поза трупа**, остаётся на экране | кадр 3 = финал |
| 7 | `hero_emerge` | появление в начале игры: выбирается из-под земли/поднимается на ноги; кадр 3 стоит | кадр 3 = стоит |
| 8 | `hero_build` | достраивает здание: стучит молотком, руки заняты; цикл 4 кадра | цикл |
| 9 | `hero_carry_walk` | идёт вправо и несёт что-то двумя руками перед собой на уровне груди, **предмет не рисовать** (кубик рисует игра, оставьте руки в позе «держит»); цикл | нет |
| 10 | `hero_loot` | открывает сундук: 0 наклон, 1 открывает крышку, 2 берёт, 3 выпрямляется с добычей (добыча не рисуется); **кадр 3 = момент подбора** | кадр 3 |

Промпт для полосы (`{ACTION}` из таблицы):

```
[DAY] Animation strip: exactly 4 equal square cells in one row on a flat solid
#FF00FF background, frames left to right. The attached reference character, facing
right, performing: {ACTION}. Same character, costume, colors, proportions and
outline weight in all four frames, same scale as the attached reference, feet on the
same ground line in every frame, body centered in each cell. Each frame is a clearly
different keypose. Matte hand-painted 3D look. No text, no numbers, no grid lines,
no ground shadow.
```

## 5. Монстры

Всем: STYLE `NIGHT`, зловеще-милый стиль (крупные глаза, читаемый силуэт, без ужасов и крови), цвет глаз или свечения по таблице. Рисуется **лицом вправо**.

Рефы: реф-лист монстра (п. ниже) + `refs/ref-night-layout.png` (гоблин, скелет, слайм как стилевой эталон).

### Реф-лист монстра (`<имя>_ref`, 3 варианта)

```
[NIGHT] Monster character reference sheet on a flat solid {KEY} background: {BRIEF}.
Three poses side by side, all facing right: neutral standing, mid-move, and attack
pose. Chunky rounded shapes, matte hand-painted 3D look, same outline weight in
every pose, readable silhouette. Cute-menacing, no gore, no blood. No text, no
labels, no grid.
```

### Полосы монстра

Ряды исходного листа монстров (правый вариант зеркалится Claude):

| Ряд | ID полосы | Что нарисовать (4 кадра) |
|---|---|---|
| 1 (→2) | `<имя>_walk` | ход/скольжение вправо, цикл из 4 разных поз (для парящих: покачивание вверх-вниз с наклоном) |
| 3 (→4) | `<имя>_attack` | по типу атаки (см. таблицу «Атака») |
| 5 (→6) | `<имя>_die` | падение/распад: 0 удар, 1 оседает, 2 разваливается/тает, 3 **финальная поза трупа** (остаётся на экране 5 секунд, затем исчезает) |
| 7 (→8) | `lich_spell` | только лич: замах, **кадр 3 = выброс заклинания** |

Ряд 0 (idle) у монстров в игре не используется, не рисовать.

**Атака: где ключевой кадр.**

| Тип | Кто | Ключевой кадр |
|---|---|---|
| Melee | zombie, hauntedArmour, demon, earthElemental, lich | кадр **1** = удар попадает, кадр 3 = возврат |
| Fast (двойной удар) | rat, spider, imp, waterElemental | удары на кадрах **1 и 3** (два быстрых выпада) |
| Ranged | skeleton (стрела), lizardman (стрела), fireElemental (огненный шар), warlock (огненный шар) | кадр **3** = выпуск снаряда (кадры 0–2 замах/прицел). Снаряд рисуется отдельно (04) |
| Spell | lich | кадр **3** = заклинание |

### Бриф и размеры (в игре)

Логическая клетка W×H дана для справки: пропорции рисуем такие же, размер ячейки по п. 2 (S или L).

| Имя | W×H | Класс | Ключ | BRIEF |
|---|---|---|---|---|
| `zombie` | 16×32 | S | `#FF00FF` | a ragged green-skinned zombie, torn brown clothes, arms forward, shuffling, dim green glow in the eyes |
| `hauntedArmour` | 70×49 | L | `#FF00FF` | an empty suit of medieval armor with a big sword floating slightly above the ground, glowing green-blue eyes in the helmet |
| `demon` | 72×86 | L | `#00FFFF` | a large horned demon, dark red skin, bat wings folded, small flames around the horns, glowing orange eyes |
| `rat` | 40×13 | S | `#FF00FF` | a big brown rat with a long tail, red glowing eyes, low to the ground |
| `spider` | 60×38 | L | `#FF00FF` | a large dark spider with long legs, six red eyes, low and wide |
| `waterElemental` | 53×39 | L | `#FF00FF` | a living blob of blue water with two bright eyes, drips and small waves at the base |
| `imp` | 30×60 | S | `#00FFFF` | a small red imp with tiny bat wings, pointed tail and horns, a mischievous grin, hovering slightly |
| `skeleton` | 27×32 | S | `#FF00FF` | a skeleton archer with a cracked skull, a wooden bow, dim violet glow in the eye sockets |
| `lizardman` | 32×35 | S | `#FF00FF` | a green lizardman archer with a short bow, scaly skin, yellow eyes, tail |
| `fireElemental` | 30×41 | S | `#00FFFF` | a living flame with a small face, orange and yellow, a lick of fire for arms |
| `warlock` | 24×37 | S | `#00FF00` | a hooded dark warlock with a gnarled staff, violet magic glowing under the hood |
| `earthElemental` | 58×74 | L | `#FF00FF` | a big moss-covered stone golem, glowing green eyes, heavy fists |
| `lich` | 41×60 | L | `#00FF00` | a crowned skeletal lich in tattered dark robes, staff with a red crystal, glowing red eyes, hovering |

Промпт полосы монстра: как в п. 4, но `[NIGHT]`, `The attached monster reference sheet, facing right, performing: {ACTION}`, ключ из таблицы.

`ACTION` по типу:

- walk: `moving to the right in a 4-frame cycle (frame 1 and 3 are contact poses, 2 and 4 are passing poses; floating monsters bob up and down)`
- die: `dying: frame 1 hit and recoiling, frame 2 collapsing, frame 3 breaking apart or melting, frame 4 a low final corpse pose lying on the ground`
- attack (melee): `a melee attack: frame 1 wind-up, frame 2 the strike at full extension, frame 3 follow-through, frame 4 recovering`
- attack (fast): `two quick strikes: frame 1 wind-up, frame 2 first strike, frame 3 wind-up again, frame 4 second strike`
- attack (ranged): `aiming and shooting: frame 1 raising the weapon, frame 2 drawing/aiming, frame 3 releasing the shot, frame 4 lowering it (draw no projectile)`
- lich_spell: `casting a spell: frame 1 raising the staff, frame 2 gathering red energy, frame 3 releasing the spell with a burst of glow, frame 4 lowering the staff`

## 6. Дракон (после подтверждения Claude)

Дракон в игре собран из **деталей**: тело (спрайт-лист), шея из сегментов и голова. Шею и голову игра сама поворачивает и сгибает кодом. Тело ставится справа и смотрит **влево** (на героя), зеркальный вариант слева.

| Деталь | Логически | Ячейка | Что нарисовать |
|---|---|---|---|
| Тело, 5 рядов × 4 кадра | 204×164 | 1536×1280 | смотрит **влево**; **без шеи и головы** (шея крепится слева спереди у груди) |
| Голова | 81×30 | 768×288 | **3 позы**: рот закрыт, приоткрыт, широко открыт (вправо и влево зеркалом) |
| Сегмент шеи | 24×24 | 256×256 | 1 чешуйчатый сегмент, стыкуется в цепочку |

Ряды тела (Claude подтвердит соответствие кодом перед началом):

| Ряд | Действие |
|---|---|
| 0 | сидит на земле, идле: дыхание, взмах хвоста |
| 1 | летит: взмах крыльями, цикл |
| 2 | приземляется: складывает крылья, оседает (кадры 0–3) |
| 3 | замах крыльями (для WingBuffet) |
| 4 | удар крыльями (порыв) |

STYLE `NIGHT`, драматично: тёмно-красный и угольный дракон, гребень на спине, крылья с перепонками, светящиеся жилки, тёплый свет из пасти. Свет на фоне `bg_dragon_*`.

Промпты: реф-лист дракона (вид сбоку, 3 позы), затем детали по образцу п. 4. Рядом рисуются отдельно огненный шар, ледяной луч, огненный вал (04-icons-and-misc.md).

Пока Claude не подтвердил состав, дракона **не рисовать**.

## 7. Сборка (делает Claude)

1. Нормализация: по кадру 0 полосы `walk` (стойка) вычисляется масштаб и линия земли, все кадры приводятся к одному масштабу и центрируются по телу. Кадры одной полосы не должны «плыть».
2. Левые ряды = зеркало правых. Итоговый порядок рядов совпадает с оригиналом, чтобы `updateSprite` (`graphics.js:686`) работал без изменений: `x = frame × ширина_клетки`, `y = ряд × высота_клетки`.
3. **Лист на каждого персонажа отдельным файлом**, не общий `monsters.png`. Общий лист при ×3 получил бы высоту около 15 000 px, больше лимита текстуры телефона (4096–8192). Для этого правится `sprites.js` (имя → файл и смещение 0).
4. Ночной слой героя (`dudenight`) больше не нужен: одна цветная раскраска.
5. Клетка героя в игре расширяется для взмаха меча; хитбокс отвязывается от ширины клетки (`getHitboxWidth`).
6. Проверка в браузере: ходьба, удар (урон на кадре 1), выстрел (снаряд на кадре 3), смерть (труп остаётся), зеркало.

## 8. Чек-лист для агента

- [ ] `hero_ref` ×3, 🛑 Гейт 3
- [ ] 9 полос героя, 🛑 Гейт 3a
- [ ] `zombie`, `skeleton`: реф-лист + walk/attack/die, 🛑 Гейт 3b
- [ ] `hauntedArmour`, `demon`, `rat`, `spider`, `waterElemental`, `imp`, `lizardman`, `fireElemental`, `warlock`, `earthElemental`: по 3 полосы
- [ ] `lich`: walk/attack/die + `lich_spell`
- [ ] дракон (только после подтверждения)
- [ ] все записаны в `out/LOG.md`

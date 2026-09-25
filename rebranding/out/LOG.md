# Журнал генерации

Формат строки: `id | файл | реф(ы) | ключ фона или alpha | заметка | статус`
Статусы: `pending` (агент), `approved` или `redo: <причина>` (ревью Claude).

frame_day | out/env/frame/frame_day_v1.png | ref-day-layout | #FF00FF | terra/medium; рамка вытянута по вертикали, проём не квадрат | redo: не квадрат
frame_day | out/env/frame/frame_day_v2.png | ref-day-layout | #FF00FF (ключ неровный, ~251,3,251) | лучший: симметрия, чистая верхняя балка, лоза слева и внизу. Замер: внешний 1934×1790, проём 1300×1225, толщина ~300 px вместо 144 | pending (кандидат, нужна правка пропорций)
frame_day | out/env/frame/frame_day_v3.png | ref-day-layout | alpha+#FF00FF | лоза лезет на верхний левый угол, толщина неравномерная (270–361), внешний 1990×1855 | redo: лоза на углу, не квадрат
floor_day | out/env/floor/floor_day_v1.png | ref-day-tiles | нет | ровная песочная текстура, без сетки | pending
floor_day | out/env/floor/floor_day_v2.png | ref-day-tiles | нет | чуть контрастнее v1 | pending
socket_day | out/env/floor/socket_day_v1.png | ref-day-tiles | нет (alpha=255 везде, белый фон) | лунка тяжёлая, с тёмной каймой по внешнему краю | redo: фон белый, не прозрачный
socket_day | out/env/floor/socket_day_v2.png | ref-day-tiles | #FF00FF (чистый, 255,0,255) | 1024×1024, чистый ключ, мягкая лунка, тёмной каймы почти нет | pending
frame_day | out/env/frame/frame_day_fit.png | frame_day_v2 | alpha | tools/fit_frame.py: ключ в альфу, кусочная подгонка: внешний 32..2015, проём 332..1715 (квадрат, толщина 300) | approved (пользователь выбрал v2, подгонка)
floor_day | out/env/floor/floor_day_v2.png | ref-day-tiles | нет | выбрана пользователем | approved
socket_day | out/env/floor/socket_day_v2.png | ref-day-tiles | #FF00FF | принята | approved
frame_night | out/env/frame/frame_night_v1.png | frame_day_fit, ref-night-layout | #FF00FF/alpha | верхняя балка тоньше, правая колонна уже | redo: геометрия (маска IoU 0.989)
frame_night | out/env/frame/frame_night_v2.png | frame_day_fit, ref-night-layout | #FF00FF | лучшая: тёмная кладка, железные уголки, лоза как днём; маска IoU с днём 0.995, проём 0.999 | pending (кандидат)
frame_night | out/env/frame/frame_night_v3.png | frame_day_fit, ref-night-layout | #FF00FF/alpha | геометрия точная (33..2015, проём 333..1715), но светлее и холоднее, менее контрастная кладка | pending (запасная)
frame_night | out/env/frame/frame_night_fit.png | frame_night_v2 | alpha | tools/fit_frame.py, та же геометрия что frame_day_fit | pending
floor_night | out/env/floor/floor_night_v1.png | floor_day_v2, ref-night-tiles | нет | сильная мозаика пятен, светлее, шумно под плитками | pending
floor_night | out/env/floor/floor_night_v2.png | floor_day_v2, ref-night-tiles | нет | спокойная, низкий контраст, трещин почти не видно | pending (рекомендуется)
socket_night | out/env/floor/socket_night_v1.png | socket_day_v2, ref-night-tiles | #FF00FF | 1024×1024, ключ чистый, тёплый рим-свет снизу справа | pending
mock_field | out/env/mock_field_v1.png | frame_*_fit, floor_*, socket_* | нет | мок: день, ночь с floor v2, ночь с floor v1; 8×8 лунок | pending
frame_night | out/env/frame/frame_night_fit.png | frame_night_v2 | alpha | выбрана пользователем | approved
floor_night | out/env/floor/floor_night_v2.png | floor_day_v2, ref-night-tiles | нет | выбрана пользователем | approved
socket_night | out/env/floor/socket_night_v1.png | socket_day_v2 | #FF00FF | принята вместе с набором | approved
bg_s1_day_land | out/env/bg/bg_s1_day_land_v1.png | ref-day-layout | нет | terra/medium, 3840×2160; в центре виден посёлок и озеро, контраст выше, передний план тяжёлый | redo: центр не пустой
bg_s1_day_land | out/env/bg/bg_s1_day_land_v2.png | ref-day-layout | нет | центр спокойный (холмы, дымка), мельница слева, дома по бокам, мягкая глубина резкости | approved (выбор Claude, ждёт подтверждения на гейте)
bg_s1_night_land | out/env/bg/bg_s1_night_land_v1.png | bg_s1_day_land_v2, ref-night-layout | нет | 3840×2160; та же сцена (мельница, дома, дорога, горы), луна, тёплые окна; центр спокойный, у озера мелкие огни | pending
bg_s1_day_port | out/env/bg/bg_s1_day_port_v1.png | bg_s1_day_land_v2 | нет | 1440×3120; та же сцена; в полосе 25–75% есть деревья и озеро (вместо чистой дымки), но её закрывает доска; сверху мельница и дома выглядят парящими островками | pending
bg_s1_night_port | out/env/bg/bg_s1_night_port_v1.png | bg_s1_night_land_v1, bg_s1_day_port_v1 | нет | 1440×3120; композиция как у day_port, гамма ночи выдержана | pending
mock_bg | out/env/mock_bg_v1.png | frame_*_fit, floor_*, socket_*, bg_s1_* | нет | поле поверх фона: land день/ночь, port день/ночь; рамка при opening=доска шире экрана (толщина 300 px) | pending
frame_day | out/env/frame/frame_day_thin_v1.png | гайд-кольцо, ref-day-layout | #FF00FF | не квадрат (проём 1761×1761, но смещён, левая/правая толщина 118) | redo: геометрия
frame_day | out/env/frame/frame_day_thin_v2.png | гайд-кольцо (толщина 150), ref-day-layout | #FF00FF | геометрия точная: внешний 32..2015, проём 182..1865, толщина 150 на всех сторонах; лоза слева и в нижних углах, верхняя балка чистая | approved
frame_day | out/env/frame/frame_day_thin_fit.png | frame_day_thin_v2 | alpha | tools/fit_frame.py in out 182 1866 (рамка вдвое тоньше по решению пользователя, прежние frame_*_fit.png с толщиной 300 устарели) | approved
frame_day | out/env/frame/frame_day_thin_v3.png | гайд-кольцо | #FF00FF | левая полоса толще (175 против 150), лоза заходит на левый край | redo: геометрия
bg_s1 | (решение пользователя) | - | - | фон в 3 слоя: дальний / средний / передний; мастер 2:1 4320×2160 (port 1:2 1440×2880 по умолчанию); средний план приглушённый, не отвлекает от поля; блюр запекаем потом, оригиналы храним; полноэкранные bg_s1_*_v* остаются как референс сцены | approved
frame_night | out/env/frame/frame_night_thin_v1.png | frame_day_thin_fit, ref-night-layout | #FF00FF | тонкая, толщина 150, маска IoU с днём 0.9875, проём 0.9988; каменная кладка, железные уголки, лоза как днём | approved (выбор Claude, ждёт подтверждения)
frame_night | out/env/frame/frame_night_thin_v2.png | то же | #FF00FF | сдвиг по внешнему краю (маска IoU 0.956), мелкий мусор у проёма | redo: геометрия
frame_night | out/env/frame/frame_night_thin_v3.png | то же | #FF00FF | чистая кладка, но маска IoU 0.971, левая толщина неравномерна | pending (запасная)
frame_night | out/env/frame/frame_night_thin_fit.png | frame_night_thin_v1 | alpha | tools/fit_frame.py in out 182 1866 | approved (с v1)
bg_s1_far_day | out/env/bg/bg_s1_far_day_land_v1.png | bg_s1_day_land_v2, ref-day-layout | нет | 4320×2160, небо/горы/дали/озеро, без построек и кустов | pending
bg_s1_far_night | out/env/bg/bg_s1_far_night_land_v1.png | far_day, ref-night-layout | нет | луна, звёзды, та же геометрия гор и озера | pending
bg_s1_mid_day | out/env/bg/bg_s1_mid_day_land_v1.png | far_day, bg_s1_day_land_v2 | #FF00FF | средний слой на уровне доски: 2 домика слева/справа, дорога, трава, растения; центр 75% прозрачный | pending
bg_s1_mid_night | out/env/bg/bg_s1_mid_night_land_v1.png | mid_day, far_night | #FF00FF | ночная версия, тёплые окна | pending
fg_day_land | out/env/fg/fg_day_land_v1.png | bg_s1_day_land_v2 | #FF00FF | общий передний план на все этапы: листья, цветы, камни по углам, центр 100% прозрачный; на краях боке слабая розовая кайма (лечится tools/key_layer.py) | pending
fg_night_land | out/env/fg/fg_night_land_v1.png | bg_s1_night_land_v1, ref-night-layout | #FF00FF | листва, руины с фонарём и факелом | pending
mock_layers_s1 | out/env/mock_layers_s1_v1.png | все слои s1, тонкие рамки, floor v2, socket | нет | 3 слоя + поле: день и ночь | pending
bg_s2_far_day | out/env/bg/bg_s2_far_day_land_v1.png | far s1 / far_day s2 | нет | 4320×2160, дальний слой этапа 2, без ближних построек | pending
bg_s2_mid_day | out/env/bg/bg_s2_mid_day_land_v1.png | far day s2, mid s1 | #FF00FF | средний слой на уровне доски, центр пуст, полоса травы внизу | pending
bg_s2_far_night | out/env/bg/bg_s2_far_night_land_v1.png | far s1 / far_day s2 | нет | 4320×2160, дальний слой этапа 2, без ближних построек | pending
bg_s2_mid_night | out/env/bg/bg_s2_mid_night_land_v1.png | far night s2, mid s1 | #FF00FF | средний слой на уровне доски, центр пуст, полоса травы внизу | pending
bg_s3_far_day | out/env/bg/bg_s3_far_day_land_v1.png | far s1 / far_day s3 | нет | 4320×2160, дальний слой этапа 3, без ближних построек | pending
bg_s3_mid_day | out/env/bg/bg_s3_mid_day_land_v1.png | far day s3, mid s1 | #FF00FF | средний слой на уровне доски, центр пуст, полоса травы внизу | pending
bg_s3_far_night | out/env/bg/bg_s3_far_night_land_v1.png | far s1 / far_day s3 | нет | 4320×2160, дальний слой этапа 3, без ближних построек | pending
bg_s3_mid_night | out/env/bg/bg_s3_mid_night_land_v1.png | far night s3, mid s1 | #FF00FF | средний слой на уровне доски, центр пуст, полоса травы внизу | pending
bg_s4_far_day | out/env/bg/bg_s4_far_day_land_v1.png | far s1 / far_day s4 | нет | 4320×2160, дальний слой этапа 4, без ближних построек | pending
bg_s4_mid_day | out/env/bg/bg_s4_mid_day_land_v1.png | far day s4, mid s1 | #FF00FF | средний слой на уровне доски, центр пуст, полоса травы внизу | pending
bg_s4_far_night | out/env/bg/bg_s4_far_night_land_v1.png | far s1 / far_day s4 | нет | 4320×2160, дальний слой этапа 4, без ближних построек | pending
bg_s4_mid_night | out/env/bg/bg_s4_mid_night_land_v1.png | far night s4, mid s1 | #FF00FF | средний слой на уровне доски, центр пуст, полоса травы внизу | pending
mock_layers_s2-s4 | out/env/mock_layers_s2-s4_v1.png | far+mid s2..s4 | нет | слева far+mid, справа mid на сером; строки: s2 день/ночь, s3 день/ночь, s4 день/ночь | pending
frame_night | out/env/frame/frame_night_thin_v1.png | frame_day_thin_fit | #FF00FF | подтверждена пользователем | approved
fg_day_land | out/env/fg/fg_day_land_v1.png | - | #FF00FF | листья обрезаны по прямым вертикалям из-за формулировки «центр 50% пустой» | redo: прямые края (пользователь), новый промпт без прямоугольной границы, запрос настоящей прозрачности (v2)
fg_night_land | out/env/fg/fg_night_land_v1.png | - | #FF00FF | та же причина | redo: прямые края
transparency | - | - | - | проверено: все прежние файлы имеют alpha=255 везде, потому что в промптах требовался сплошной #FF00FF; встроенный imagegen умеет настоящую прозрачность, тест на fg_*_land_v2 | тест
fg_day_land | out/env/fg/fg_day_land_v2.png | bg_s1_day_land_v2 | настоящая alpha | 4320×2160; прозрачно 69%, мягкие края, нет прямых срезов, без розового | approved (Claude, ждёт подтверждения)
fg_night_land | out/env/fg/fg_night_land_v2.png | bg_s1_night_land_v1 | настоящая alpha | 4320×2160; прозрачно 68%, руины с фонарём и факелом; края без полупрозрачности (жёсткая альфа), проверить при блюре | approved (Claude)
transparency | - | - | - | итог теста: built-in image_gen отдаёт настоящую alpha, если просить «genuinely transparent background» и не требовать цвет; дальше используем её для средних слоёв, переднего плана, рамок, лунок | решение
bg_sN_far_{day,night}_port | out/env/bg/bg_s{1..4}_far_{day,night}_port_v1.png | far land того же этапа | нет | 1440×2880, горизонт ~62%, сцена совпадает с land | pending
bg_sN_mid_{day,night}_port | out/env/bg/bg_s{1..4}_mid_{day,night}_port_v1.png | far port того же этапа, mid land | настоящая alpha | 1440×2880; средний слой внизу: трава, домики по бокам, центр прозрачный; s1, s2, s4 и все ночные ок | pending
bg_s3_mid_day_port | out/env/bg/bg_s3_mid_day_port_v1.png | far port, mid land | настоящая alpha | 23% полупрозрачных пикселей, слой как бледная дымка, домики почти не видны | redo: дымка, нужна плотная непрозрачная живопись (v2)
fg_day_port | out/env/fg/fg_day_port_v1.png | fg_day_land_v2 | настоящая alpha | 1440×2880, крупные кусты по нижним углам закрывают домики среднего слоя | redo: компактнее (v2)
fg_night_port | out/env/fg/fg_night_port_v1.png | fg_night_land_v2 | настоящая alpha | 1440×2880, руины и факелы по нижним углам, листва вверху, средняя полоса пуста | pending
mock_port | out/env/mock_port_v1.png | все слои портрета, тонкие рамки, floor v2 | нет | схематично: положение доски условное, без HUD | pending
bg_s3_mid_day_port | out/env/bg/bg_s3_mid_day_port_v2.png | far_day_port s3, mid land s3, mid_day_port s2 | настоящая alpha | 1440×2880; плотная живопись, полупрозрачных 0.5%, башня и дома с красной и синей крышей хорошо видны | approved (Claude)
fg_day_port | out/env/fg/fg_day_port_v2.png | fg_day_land_v2, fg_day_port_v1 | настоящая alpha | 1440×2880; компактная листва по углам, прозрачно 84%, домики среднего слоя видны | approved (Claude)
mock_port_day | out/env/mock_port_day_v2.png | s3, s1, s2, s4 день | нет | портретный день с исправленными s3 mid и fg v2 | pending
layout | - | www/css/main.css | - | портрет: сцена-колонка = полоса мира 110 + доска + инвентарь/магия ~50 (почти весь экран); слева от доски нужна панель сердец, справа панель уровня; фон виден лишь в полосах над и под колонкой | справка для встраивания
fg_day_port | out/env/fg/fg_day_port_v2.png | fg_day_land_v2 | настоящая alpha | листва сверху мешает, снизу заползает на доску | redo: сверху ничего, снизу маленькие пучки в углах (v3)
fg_night_port | out/env/fg/fg_night_port_v1.png | fg_night_land_v2 | настоящая alpha | листва сверху мешает | redo: сверху ничего, снизу маленькие пучки (v2)
fg_day_port | out/env/fg/fg_day_port_v3.png | fg_day_land_v2 | (ожидалась alpha) | кодекс заявил real alpha, факт: alpha=255 везде, белый фон 94% (замер) | redo: прозрачность не сработала
fg_night_port | out/env/fg/fg_night_port_v2.png | fg_night_land_v2 | (ожидалась alpha) | то же, белый непрозрачный фон | redo: прозрачность не сработала
transparency | - | - | - | вывод: «genuinely transparent» срабатывает не всегда; кодекс сам не проверяет. Правило: после каждой генерации замерять alpha (min<10, доля прозрачных > 0), при провале переключаться на ключ #FF00FF + tools/key_layer.py | правило
fg_day_port | out/env/fg/fg_day_port_v4.png | fg_day_land_v2 | #FF00FF | сверху ничего, два маленьких пучка внизу (контент только в нижних 10% кадра) | approved (Claude)
fg_day_port | out/env/fg/fg_day_port_v4_a.png | fg_day_port_v4 | alpha | tools/key_layer.py; прозрачно 95.8% | approved (Claude)
fg_night_port | out/env/fg/fg_night_port_v3.png | fg_night_land_v2 | #FF00FF | сверху ничего, внизу пучки с фонарём и факелом (контент с 81% высоты) | approved (Claude)
fg_night_port | out/env/fg/fg_night_port_v3_a.png | fg_night_port_v3 | alpha | tools/key_layer.py; прозрачно 91.8% | approved (Claude)
mock_port | out/env/mock_port_v4.png | s1, s3 день; s1, s4 ночь | нет | реальная колонка сцены (мир 110 + доска), фон виден сверху и снизу; листва не заходит на доску | pending
hud | out/icons/hud/{heart_socket_day,heart_socket_night,heart_fill,slot_ring_day,slot_ring_night,inventory_plank_day,inventory_plank_night,bar_frame_day,bar_frame_night}_v1.png | ref-day-layout, ref-night-layout, дневные как реф для ночных | #FF00FF | 9 файлов HUD, по 1 варианту (по плану 3, для мока хватило); ключ чистый; день дерево+латунь, ночь камень+железо, геометрия пар совпадает | pending (гейт 4)
loot | out/icons/loot/loot_{health,mana}_potion_v1.png | ref-night-layout | #FF00FF | красное и синее зелье | pending
spells | out/icons/spells/spell_{haste,freeze_time,phase_change}_v1.png | ref-night-layout | #FF00FF | сапог с крылом, секундомер во льду, солнце и месяц | pending
hud_keyed | out/icons/keyed/*.png | выше | alpha | tools/key_layer.py, прозрачно 44–84% | pending
mock_all | out/env/mock_all_{desktop,portrait}_{day,night}.png | все слои s1 + рамка + подложка + лунки + HUD | нет | общий вид 1920×1080 и 390×844; в портрете сердца и опыт на рельсах рамки; нет: полоса мира, здания, плитки, герой (не сгенерированы); скрипт tools/mock_all.py | pending
mock_all | out/env/mock_all_{desktop,portrait}_{day,night}.png | правки пользователя | нет | (1) сердца и полоса опыта сидят на рельсе рамки внутри краёв, столбик плотный (шаг = размер − 2), заливка сердца 0.9 от полости; (2) сетка лунок: зазор между лунками = отступу от бортика, лунки крупнее (без прозрачных полей сокета) | pending
hud | out/icons/hud/panel_plate_{day,night}_v1.png | inventory_plank_{day,night}_v1 | #FF00FF | 1536×512, пустая плашка того же стиля, что панель инвентаря (дерево+латунь / камень+железо, уголки с заклёпками), без лунок; 9-slice для любых панелей | pending
hud | out/icons/hud/vine_wrap_{day,night}_v1.png | frame_day_thin_v2 / vine_wrap_day | #FF00FF | 512×1536, вертикальная лиана, ночью темнее и синее, форма совпадает | pending
mock_all | out/env/mock_all_{desktop,portrait}_{day,night}.png | правки пользователя 2 | нет | десктоп: сердца и опыт на отдельных панелях из panel_plate (толщина = высота панели инвентаря), у сердец лиана; портрет: на рельсе рамки; заливка сердца подобрана по центроиду полости (внутри, запас 8%); лунки крупнее: видимый габарит, зазор = отступ от бортика = 5% шага | pending
socket_day | out/env/floor/socket_day_v3_1.png | socket_day_v2, ref-day-tiles | #FF00FF | тонкий ободок, но габарит перекошен (108..940 × 91..909) | redo: не квадрат
socket_day | out/env/floor/socket_day_v3_2.png | socket_day_v2, ref-day-tiles | #FF00FF | тонкий аккуратный ободок (~4% стороны), углубление ~88% ширины (было ~78%), габарит 868×863 | approved (Claude, по замечанию пользователя «ободок тоньше, место под плитки»)
code | www/js/app/loot.js, graphics/loot.js, gamecontent.js, css/main.css:2211-2270 | - | - | заряды: у обычных предметов max 3 (3 кружка: слева-снизу, по центру ниже, справа-снизу), у large (callDragon) max 1 (один кружок по центру); видов предметов 5 (healthPotion, manaPotion, bomb, equipment, callDragon), кнопка появляется, когда предмет найден, значит панель инвентаря 1..5 слотов | справка
mock | out/archive/mocks/{mock_field_v1,mock_bg_v1,mock_layers_s1_v1,mock_layers_s2-s4_v1,mock_port_day_v2,mock_port_v1,mock_port_v3,mock_port_v4}.png | - | - | устаревшие моки (толстая рамка, старые лунки, одиночные фоны, промежуточные портреты) перенесены в архив; строки о них выше в журнале остаются как история | архив
mock | out/env/mock_all_{desktop,portrait}_{day,night}.png | актуальные ассеты этапа 1 | нет | общий вид: 3 слоя, тонкая рамка, лунки v3_2 / night_v2, панели сердец (растёт, с лианой), опыта (врез на плашке), инвентаря (1..5 слотов, кружки зарядов 3 или 1), магия; порядок: фон, средний план, поле, передний слой, HUD поверх; tools/mock_all.py | pending
mock | out/env/mock_stages_{desktop,portrait}.png | актуальные ассеты этапов 1-4 | нет | обзор этапов s1..s4, день и ночь, десктоп 2×4 и портрет 8 в ряд | pending
mock | out/env/mock_{hearts,inventory}_growth_{day,night}.png | панели | нет | рост панели сердец (3, 9, 14) и инвентаря (1..5 слотов) | pending
socket_night | out/env/floor/socket_night_v2.png | socket_day_v3_2, socket_night_v1 | #FF00FF | тонкий ободок как у дня, навy-сланец | approved (Claude)
loot | out/icons/loot/loot_{bomb,equipment,dragon_scroll}_v1.png | ref-night-layout | #FF00FF | бомба, набор для ремонта, свиток с драконом | pending
mock | out/env/mock_all_portrait_{day,night}.png, mock_stages_portrait.png | - | - | правка: в портрете старый жёлоб bar_frame заменён на скруглённый врез с золотой заливкой прямо на рельсе рамки (как в десктопе); из tools/mock_all.py удалён устаревший xpbar | pending
fg_day_land | out/env/fg/fg_day_land_v3.png | fg_day_land_v2 | настоящая alpha | левая половина сдвинута влево на 430 px (мастер 4320) tools/shift_layer.py, правая без изменений; передний план больше не подползает к слотам магии и панели сердец; v2 сохранён | approved (Claude, по замечанию пользователя)
plate_day | out/tiles/plate/plate_day_v{1,2,3}.png | ref-day-tiles | #FF00FF | 512×512, плашка ~84% холста, без внешней тени, матовая тёплая; v1 ближе всего к эталону (ровная), v2 темнее с трещинками, v3 светлее | pending (гейт 1; рекомендую v1)
plate_night | out/tiles/plate/plate_night_v{1,2,3}.png | ref-day-tiles, ref-night-tiles | #FF00FF | 512×512, навy-сланец, холодный ободок сверху-слева; слегка блестят, v2 самая матовая | pending (гейт 1; рекомендую v2 или v3)
anchors | out/tiles/anchors/{grain,wood,stone,clay,mana}_1_v{1,2,3}.png | ref-day-tiles | #FF00FF (mana #00FF00) | 15 якорей, стиль эталона совпал; сбои сети image_gen у 6 файлов, перезапуск gen_tiles1.sh (skip существующих) доделал | pending (гейт 1; выбор v2)
anchors | out/tiles/anchors/cloth_1_v{1,2,3}.png | ref-day-tiles | #FF00FF | ключ #FF00FF съедает фиолетовый: v1 вырезалась целиком, у v2/v3 25–47% полупрозрачных | redo: ключ #00FF00 (v4–v6)
anchors | out/tiles/anchors/cloth_1_v{4,5,6}.png | ref-day-tiles | #00FF00 | ткань фиолетовая, мягкие складки; v4 клубок нити, v5/v6 скрученное волокно с кремовыми бликами | pending (гейт 1; выбор v5)
tool | tools/key_layer.py | - | - | добавлен 3-й аргумент: hex ключа (по умолчанию FF00FF). Правило: фиолетовое/розовое (ткань, мана) только на #00FF00 | справка
tool | tools/compose_tiles.py, out/tiles/keyed/ | - | alpha | compose(plate, icon): обрезка по bbox, вписывание 66% плашки, выше центра на 2%, лёгкая тень; keyed/ = плашки и якоря с альфой (прозрачно 24–81%, полупрозрачных 0.5–2.4%) | справка
mock | out/tiles/mock_gate1_{classes,grid,night_plates}.png | plate_day_v1 + якоря v2 (ткань v5) | нет | 6 классов крупно / 52 / 60 px / в сером; сетка 8×7 на floor_day_v2 | pending (гейт 1). В сером clay и stone схожи (два тёмных бугра), различает фактура граней
anchors | out/tiles/anchors/cloth_1_v{4,5,6}.png | ref-day-tiles | #00FF00 | клубок/скрученное волокно | redo: пользователь: «не выглядит как ткань», нужны полотна сначала, рулоны потом
anchors | out/tiles/anchors/cloth_1_v{7,8,9}.png | ref-day-tiles | #00FF00 | сложенное фиолетовое полотно с кремово-лавандовой полосой (как полотенце на эталоне); читается как ткань и на 52 px; v8 полнее всего, v7 красивые складки, v9 плотнее и темнее; полупрозрачных 0.7–1.5% | pending (гейт 1; выбор v8)
doc | 02-tiles.md | - | - | ряд cloth: 1 сложенное полотно, 2 стопка полотен, 3 рулон с лентой, 4 два рулона с золотой каймой (решение пользователя) | справка
mock | out/tiles/mock_gate1_{classes,grid}.png | plate_day_v1, якоря v2, cloth v8 | нет | обновлены под новую ткань | pending (гейт 1)
plate_night | out/tiles/plate/plate_night_v2.png | - | #FF00FF | ночная плашка | approved (пользователь, «Ночная v2 ок»)
gate1 | plate_day_v1, {grain,wood,stone,clay,mana}_1_v2, cloth_1_v8 | - | - | плашка дня v1, якоря v2, ткань v8; clay остаётся комком | approved (пользователь: «1 да 2 да 3 оставляем комок»)
icons-day | out/tiles/icons-day/{grain_2-4,stone_2-9,wood_2-9,clay_2-4,cloth_2-4}_v1.png | якорь класса v2 (ткань v8) + ref-day-tiles | #FF00FF (cloth #00FF00) | T2, 25 иконок, tools/gen/gen_day_series.sh; альфа: прозрачно 59–82%, полупрозр. 0.7–2.7%; серии читаются: stone серый → тёмный с лавой → голубой лёд | pending
icons-day | cloth_3_v1, cloth_4_v1 | - | #00FF00 | сложенное с бантом / сложенное с узором, не рулоны | redo: пользователь хотел рулоны
icons-day | wood_2_v1, wood_4_v1, wood_8_v1 | - | #FF00FF | wood_2 связка досок (нужна одна), wood_4 три бревна (нужно одно), wood_8 золочёная доска как шкатулка/слиток | redo
icons-day | out/tiles/icons-day/{cloth_3,cloth_4,wood_2,wood_4,wood_8}_v{2,3}.png | якорь + ref | #FF00FF/#00FF00 | tools/gen/gen_day_redo.sh; рулоны со спиралью торца, одиночные доска и бревно, золочёная доска с текстурой дерева; прозрачно 64–86%, полупрозр. 0.6–2.0% | approved (Claude): cloth_3_v2 (рулон с полосами и лентой), cloth_4_v2 (два рулона с узором), wood_2_v2, wood_4_v2, wood_8_v2; v3 запасные
mock | out/tiles/mock_day_series.png, mock_day_redo.png | plate_day_v1 | нет | все 31 дневная иконка на плашке (якорь + серии с выбранными вариантами) | pending (утверждение серий)
note | wood_9_v1 | - | - | стопка золочёных БРЁВЕН (круглые торцы), а wood_8 теперь доска: рассинхрон семейства | к решению: перегенерировать wood_9 как стопку золочёных досок
icons-day | out/tiles/icons-day/wood_9_v{2,3}.png | wood_8_v2, wood_1_v2, ref-day-tiles | #FF00FF | tools/gen/gen_wood9.sh; стопка трёх золочёных досок в семействе wood_8, без круглых торцов и верёвок; прозрачно 53%, полупрозр. 1.5–2.0% | approved (Claude): wood_9_v3 (ровнее, ориентация как у wood_8); wood_9_v1 (стопка брёвен) заменён
mock | out/tiles/mock_day_series.png, mock_wood9.png | plate_day_v1 | нет | серии обновлены под wood_9_v3 | pending (утверждение серий)
night-anchors | out/tiles/night-anchors/{grain,stone,wood,clay,cloth,mana}_1_v{1,2,3}.png | ref-night-tiles + дневной якорь класса | #FF00FF (grain, stone, wood), #00FF00 (clay, cloth, mana) | T3, 18 файлов, tools/gen/gen_night_anchors.sh; grain надгробие с рукой и зелёным туманом, stone меч, wood круглый щит, clay нора с красными глазами, cloth череп с костями, mana кристальный череп; альфа: прозрачно 55–87%, полупрозр. 0.9–6.4% (cloth v1 6.4% = фиолетовое свечение); keyed-night/ | pending (гейт 1b)
note | night-anchors | - | - | свечение от генератора слабое, glow цвета класса добавляет сборщик; clay (тёмная нора) на тёмной плашке слабее по контрасту; cloth и mana оба черепа (по плану 02-tiles.md), различаются цветом (кость / розовый кристалл); stone v1 голубой ледяной (зарезервирован за ур. 7–9), v3 с золотой рукоятью (тоже ур. 7–9) | рекомендации: grain v1, stone v2, wood v1, clay v3, cloth v1, mana v1
mock | out/tiles/mock_night_anchors.png | plate_night_v2 | нет | 6 классов × 3 варианта на ночной плашке | pending (гейт 1b)
gate1b | night-anchors: grain_1_v1, stone_1_v2, wood_1_v1, clay_1_v3, cloth_1_v1, mana_1_v1 | - | - | ночные якоря; черепа у cloth и mana остаются | approved (пользователь: «Утверждаю»)
icons-night | out/tiles/icons-night/{grain_2-4,clay_2-4,cloth_2-4,stone_2-9}_v1.png (17) | ночной якорь класса, дневная иконка уровня, ref-night-tiles | M: grain, stone_2-3, 7-9; G: clay_2, cloth_3-4, stone_4-6; C: clay_3-4, cloth_2 | T3, tools/gen/gen_night_series.sh; keyed-night/; альфа: прозрачно 58–90%, полупрозр. 1.6–8.1% (stone_9 8.1% = halo, grain_4 7.6% = пламя, ок) | pending
icons-night | wood_2..9, dragon_{grain,clay,cloth} | - | - | НЕ сгенерированы: codex «You've hit your usage limit … try again at Sep 30th, 2026 8:58 PM» (не сеть) | blocked: до сброса лимита; перезапуск tools/gen/gen_night_series.sh доделает только недостающее (gen пропускает готовые)
note | icons-night clay_3 | - | - | «водяная капля с лицом» вышла как глиняный бугор с синим внутри, слабо читается как вода/капля | к решению: redo при следующей генерации
note | icons-night stone_2, stone_3 | - | - | почти не отличаются от stone_1 (сталь, меч с гардой, украшенная рукоять) на 52 px | к решению: терпимо, либо усилить различие
mock | out/tiles/mock_night_series.png | plate_night_v2 | нет | 17 ночных иконок + якоря 5 классов на ночной плашке (без mana: одна иконка, без wood 2–9) | pending
codex | tools/gen/*.sh, ../.claude.md | - | - | reasoning medium → low (по просьбе пользователя) | справка
icons-night | out/tiles/icons-night/wood_{2..9}_v1.png | ночной якорь wood_1_v1, дневная иконка уровня, ref-night-tiles | #FF00FF | T3, лимит сброшен, tools/gen/gen_night_series.sh; круглые деревянные щиты 2–3 (ур. 1–3 почти не различаются), тёмные геральдические 4–6, золочёные 7–9; прозрачно 54–75%, полупрозр. 1.3–2.8% | pending
icons-dragon | out/tiles/icons-dragon/dragon_{grain,clay,cloth}_v1.png | ночной якорь класса, ref-night-tiles | grain #FF00FF, clay/cloth #00FF00 | T4: вихрь с зелёным листом, ледяной кристалл, пламя; прозрачно 68–85%, полупрозр. 1.1–5.3% | pending
icons-night | out/tiles/icons-night/clay_3_v{2,3}.png | night clay_1_v3, day clay_3_v1 | #FF00FF | tools/gen/gen_clay3_night.sh; голубая водяная капля с лицом на терракотовой подставке, читается как вода | approved (Claude): clay_3_v2; v1 (глиняный бугор) заменён
mock | out/tiles/mock_night_rest.png | plate_night_v2 | нет | щиты 1–9, clay_3 v1–v3, грани дракона | pending
tiles | out/tiles/composed/*.png (65), out/tiles/sheets/tiles{,@2x,@3x}.png, tiles-manifest.json | plate_day_v1, plate_night_v2, утверждённые иконки | alpha | T5, tools/build_tiles.py (плашка + иконка + ночью glow цвета класса, кроп по bbox плашки, все грани 384×384); листы 312×988, 624×1976, 936×2964, 6 колонок × 19 рядов по 52, ряды: день 0–8, ночь 9–17, дракон 18 (кол. 0, 3, 4); проверено визуально mock_sheet_review.png | pending (ревью листа пользователем; в www/ не встроено)
tool | tools/compose_tiles.py | - | - | добавлен glow=(rgb, сила); tools/build_tiles.py: выбор вариантов и цвета glow по иконкам зашиты в словари DAY1/DAYV/NIGHT1/NIGHTV/G/GO | справка
mock | out/tiles/mock_sheet_review.png | tiles@2x | нет | лист в 2× на фоне дня и ночи | pending
icons-day | wood_b2_v{1,2}.png | wood_5_v1, wood_2_v2, wood_1_v2 | #FF00FF | tools/gen/gen_wood_b2.sh; связка из ДВУХ досок с верёвкой в стиле связки из четырёх | approved (Claude): v1 (цвет как у связки из 4), v2 светлее
wood order | tools/build_tiles.py (WOOD) | - | - | новый порядок дерева (пользователь): 1 одиночное бревно (wood_4_v2), 2 два бревна (якорь wood_1_v2), 3 три бревна (wood_3_v1), 4 доска (wood_2_v2), 5 связка 2 досок (wood_b2_v1), 6 связка 4 досок (wood_5_v1), 7–9 без изменений; wood_6_v1 (два бруса с ремнями) выведен; одиночное бревно чуть темнее двойного (остаток «тёмной» версии) | approved (пользователь, порядок); листы пересоберутся после ночных тиров
mock | out/tiles/mock_wood_order.png | plate_day_v1 | нет | ряд дерева в новом порядке (+ b2 v2) | pending
icons-night | out/tiles/icons-night/{stone_2,stone_3,wood_2,wood_3}_v{2,3}.png, stone_2_v{4,5}.png | ночной якорь класса, ref-night-tiles | stone_2 #FF00FF, stone_3 #00FF00, wood_2 #FF00FF, wood_3 #00FF00 | tools/gen/gen_night_tiers23.sh, gen_stone2_night.sh; по замечанию пользователя ур. 2–3 мечей и щитов «почти не отличаются»: ур. 2 меч = широкий тёмный листовидный клинок с бронзовой гардой и набалдашником (v5), ур. 3 меч = серебряный с крылатой гардой и рубином (v3); ур. 2 щит = железный крест и ряд заклёпок (v2), ур. 3 щит = стальной обод, шип и красно-кремовая звезда (v2); прозрачно 42–86%, полупрозр. 0.8–2.5% | approved (Claude): stone_2_v5, stone_3_v3, wood_2_v2, wood_3_v2; прежние v1 заменены
build | tools/build_tiles.py NIGHTV | - | - | листы и манифест пересобраны с новым порядком дерева и новыми ур. 2–3 | pending
mock | out/tiles/mock_night_tiers23.png, mock_night_swords.png, mock_sheet_review.png | plate_night_v2 | нет | сравнение тиров и обновлённый лист | pending

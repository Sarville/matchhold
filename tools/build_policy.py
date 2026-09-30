#!/usr/bin/env python3
"""Политики конфиденциальности по площадкам: python3 tools/build_policy.py
Пишет publish/privacy-policy/site/<площадка>/matchhold/policy/index.html (зеркало /opt/games/site на сервере)
=> https://games.sarville.online/<площадка>/matchhold/policy. vk = VK + OK. Сборка vk (build_platform.py) кладёт свою в dist/vk/policy."""
import html, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'publish', 'privacy-policy', 'site')
DATE = ('30 сентября 2026 г.', 'September 30, 2026')
CONTACT = '<a href="mailto:sarville@yandex.ru">sarville@yandex.ru</a>'

LOCAL = ('<b>Игровой прогресс.</b> Слоты сохранения и настройки (язык, громкость) хранятся локально на вашем устройстве. Мы не имеем к ним доступа; при удалении приложения или очистке данных они пропадают.',
         '<b>Game progress.</b> Save slots and settings (language, volume) are stored locally on your device. We cannot access them; they are lost if you uninstall the app or clear its data.')
NOSERVER = ('Мы не храним ваши данные на своих серверах.', 'We do not store your data on our servers.')

# name — как называть площадку; data — пункты раздела 1; third — раздел 3; keep — раздел 4; rights — раздел 5
P = {
'vk': dict(
    name=('VK и Одноклассники (VK Mini Apps, OK)', 'VK and Odnoklassniki (VK Mini Apps, OK)'),
    data=[
        ('<b>Игровой прогресс и покупка.</b> Мы получаем от платформы идентификатор пользователя (VK user id) и сохраняем на нашем сервере <code>games.sarville.online</code> ваш игровой прогресс и факт покупки «Отключить рекламу». Имя, фотографию, e-mail и другие данные профиля мы не запрашиваем и не храним. Настройки (язык, громкость) хранятся локально в браузере.',
         '<b>Game progress and purchase.</b> We receive your user identifier (VK user id) from the platform and store, on our server <code>games.sarville.online</code>, your game progress and the fact that you bought “Disable ads”. We do not request or store your name, photo, e-mail or other profile data. Settings (language, volume) are stored locally in the browser.'),
        ('<b>Реклама.</b> Рекламу показывает платформа (VK / OK) собственными средствами. Она может обрабатывать данные об устройстве, IP-адрес и рекламные идентификаторы по своим правилам; мы этими данными не управляем.',
         '<b>Ads.</b> Ads are shown by the platform (VK / OK) with its own tools. It may process device data, IP address and advertising identifiers under its own rules; we do not control that data.'),
        ('<b>Покупки.</b> Единственная покупка — «Отключить рекламу». Платёж проводит VK или OK; реквизиты вашей карты нам не передаются, мы получаем только подтверждение покупки.',
         '<b>Purchases.</b> The only purchase is “Disable ads”. The payment is handled by VK or OK; we never receive your card details, only confirmation of the purchase.')],
    third=('Мы не продаём данные. Они обрабатываются платформами VK и OK на условиях их собственных политик.',
           'We do not sell data. It is processed by VK and OK under their own policies.'),
    keep=('Данные на нашем сервере (VK user id, прогресс, факт покупки) хранятся, пока вы пользуетесь игрой. Чтобы их удалить, напишите нам на адрес из раздела 7.',
          'Data on our server (VK user id, progress, purchase status) is kept while you use the game. To have it deleted, write to us at the address in section 7.'),
    rights=('Вы можете запросить сведения о ваших данных на нашем сервере, их исправление или удаление, а также отозвать согласие. Настройки рекламы можно изменить в настройках платформы.',
            'You may ask what data we hold on our server, ask to correct or delete it, and withdraw consent. Ad settings can be changed in the platform settings.')),
'yandex': dict(
    name=('Яндекс Игры', 'Yandex Games'),
    data=[
        ('<b>Игровой прогресс.</b> Прогресс сохраняется в облаке Яндекс Игр (данные игрока через SDK платформы), настройки — локально в браузере. Профиль мы не запрашиваем: ни имя, ни фото, ни e-mail к нам не попадают. Облаком управляет Яндекс по своим правилам.',
         '<b>Game progress.</b> Progress is saved in the Yandex Games cloud (player data through the platform SDK); settings are stored locally in the browser. We do not request your profile: no name, photo or e-mail reaches us. The cloud is managed by Yandex under its own rules.'),
        ('<b>Реклама.</b> Игра показывает рекламу Рекламной сети Яндекса через SDK Яндекс Игр. Она может обрабатывать рекламный идентификатор, приблизительное местоположение по IP-адресу, сведения об устройстве. Мы не управляем этими данными; подробности — в политике Яндекса.',
         '<b>Ads.</b> The game shows ads from the Yandex Advertising Network through the Yandex Games SDK. It may process the advertising ID, approximate location from the IP address and device information. We do not control that data; see Yandex\'s policy for details.'),
        ('<b>Покупки.</b> Единственная покупка — «Отключить рекламу». Платёж проводят Яндекс Игры; реквизиты вашей карты нам не передаются.',
         '<b>Purchases.</b> The only purchase is “Disable ads”. The payment is handled by Yandex Games; we never receive your card details.')],
    third=('Мы не продаём данные. Они обрабатываются Яндексом (Яндекс Игры, Рекламная сеть Яндекса) на условиях его политик.',
           'We do not sell data. It is processed by Yandex (Yandex Games, Yandex Advertising Network) under its policies.'),
    keep=('Данные в облаке хранит Яндекс; удалить их можно средствами платформы. ' + NOSERVER[0], 'Cloud data is kept by Yandex and can be deleted with the platform\'s tools. ' + NOSERVER[1]),
    rights=('Права на данные в облаке и рекламе реализуются через Яндекс (настройки аккаунта и рекламы). У нас данных о вас нет.',
            'Your rights over cloud and ad data are exercised through Yandex (account and ad settings). We hold no data about you.')),
'rustore': dict(
    name=('приложение для Android (RuStore)', 'Android app (RuStore)'),
    data=[
        LOCAL,
        ('<b>Реклама.</b> Приложение показывает рекламу Yandex Mobile Ads. SDK может обрабатывать рекламный идентификатор устройства, приблизительное местоположение по IP-адресу, сведения об устройстве и приложении. Мы не управляем этими данными; подробности — в политике Яндекса. Приложению нужен доступ в интернет; иных разрешений для сбора персональных данных оно не запрашивает.',
         '<b>Ads.</b> The app shows Yandex Mobile Ads. The SDK may process the device advertising ID, approximate location from the IP address, and device and app information. We do not control that data; see Yandex\'s policy for details. The app needs internet access and requests no other permissions to collect personal data.'),
        ('<b>Покупки.</b> Единственная покупка — «Отключить рекламу». Платёж проводит RuStore; реквизиты вашей карты нам не передаются. Факт покупки проверяется по данным RuStore, при отсутствии сети запоминается локально.',
         '<b>Purchases.</b> The only purchase is “Disable ads”. The payment is handled by RuStore; we never receive your card details. Purchase status is checked against RuStore and cached locally when offline.')],
    third=('Мы не продаём данные. Они обрабатываются RuStore и рекламным сервисом Яндекса на условиях их политик.',
           'We do not sell data. It is processed by RuStore and Yandex\'s advertising service under their policies.'),
    keep=('Локальные данные хранятся на вашем устройстве, пока вы их не удалите. ' + NOSERVER[0], 'Local data stays on your device until you delete it. ' + NOSERVER[1]),
    rights=('У нас нет ваших данных. Настройки рекламного идентификатора можно изменить в настройках устройства, права на данные в RuStore и рекламе — через эти сервисы.',
            'We hold no data about you. The advertising ID can be reset in your device settings; rights over data held by RuStore and the ad service are exercised through them.')),
}

CSS = """  :root { --bg:#faf6ec; --fg:#2b2418; --muted:#6b5f49; --accent:#8a4b12; --card:#fffdf7; --line:#e3d9c3; }
  @media (prefers-color-scheme: dark) { :root { --bg:#1c1913; --fg:#efe7d4; --muted:#b3a88f; --accent:#e9b25b; --card:#25211a; --line:#3a3427; } }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--fg); font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }
  main { max-width:760px; margin:0 auto; padding:24px 16px 64px; }
  h1 { font-size:1.8rem; margin:.4em 0 .2em; }
  h2 { font-size:1.2rem; margin:1.6em 0 .4em; color:var(--accent); }
  p, li { margin:.5em 0; }
  ul { padding-left:1.3em; }
  nav { display:flex; gap:12px; margin:8px 0 24px; }
  nav a { padding:6px 14px; border:1px solid var(--line); border-radius:999px; color:var(--fg); text-decoration:none; background:var(--card); }
  .meta { color:var(--muted); font-size:.9rem; }
  section { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:8px 20px 16px; margin-bottom:28px; }
  .tbd { background:#fff0b3; color:#4a3a00; padding:0 .3em; border-radius:4px; }
  @media (prefers-color-scheme: dark) { .tbd { background:#5a4a10; color:#ffeaa0; } }
  a { color:var(--accent); }"""

T = {  # 0 = ru, 1 = en
    'lang': ('ru', 'en'),
    'h1': ('Политика конфиденциальности игры «Матчхолд»', 'Matchhold Privacy Policy'),
    'meta': ('Дата редакции: %s Разработчик: sarville (далее — «мы»). Площадка: %s.', 'Last updated: %s. Developer: sarville (“we”). Platform: %s.'),
    'intro': ('«Матчхолд» — игра в жанре «три в ряд» со стройкой базы. Мы стараемся собирать как можно меньше данных. Ниже — что именно обрабатывается и зачем в этой версии игры.',
              'Matchhold is a match-3 game with base building. We try to collect as little data as possible. Here is what is processed and why in this version of the game.'),
    'h': (('1. Какие данные обрабатываются', '2. Для чего используются данные', '3. Передача третьим лицам', '4. Хранение и удаление', '5. Ваши права', '6. Дети', '7. Контакты и изменения'),
          ('1. What data is processed', '2. Why the data is used', '3. Sharing with third parties', '4. Retention and deletion', '5. Your rights', '6. Children', '7. Contact and changes')),
    'no': ('Мы не используем сервисы веб-аналитики, не собираем точное местоположение, контакты и файлы.', 'We do not use web analytics services and do not collect precise location, contacts or files.'),
    'use': (('сохранять и восстанавливать ваш прогресс;', 'помнить покупку «Отключить рекламу» и отключать рекламу;', 'показывать рекламу, которая поддерживает бесплатную игру.'),
            ('to save and restore your progress;', 'to remember the “Disable ads” purchase and turn ads off;', 'to show ads that keep the game free.')),
    'kids': ('Игра рассчитана на возраст 6+ и не требует регистрации или ввода персональных данных. Мы сознательно не собираем персональные данные детей.',
             'The game is rated 6+ and needs no registration or personal data. We knowingly do not collect personal data from children.'),
    'contact': ('Связь с нами: %s. Если политика изменится, мы обновим её на этой странице и изменим дату редакции.', 'Contact: %s. If this policy changes, we will update this page and the date above.'),
}


def section(p, i):
    d = P[p]
    data = [x[i] for x in d['data']]
    h = T['h'][i]
    return '\n'.join([
        '<section id="%s" lang="%s">' % (T['lang'][i], T['lang'][i]),
        '<h1>%s</h1>' % T['h1'][i],
        '<p class="meta">%s</p>' % (T['meta'][i] % (DATE[i], d['name'][i])),
        '<p>%s</p>' % T['intro'][i],
        '<h2>%s</h2>\n<ul>\n%s\n</ul>\n<p>%s</p>' % (h[0], '\n'.join('  <li>%s</li>' % x for x in data), T['no'][i]),
        '<h2>%s</h2>\n<ul>\n%s\n</ul>' % (h[1], '\n'.join('  <li>%s</li>' % x for x in T['use'][i])),
        '<h2>%s</h2>\n<p>%s</p>' % (h[2], d['third'][i]),
        '<h2>%s</h2>\n<p>%s</p>' % (h[3], d['keep'][i]),
        '<h2>%s</h2>\n<p>%s</p>' % (h[4], d['rights'][i]),
        '<h2>%s</h2>\n<p>%s</p>' % (h[5], T['kids'][i]),
        '<h2>%s</h2>\n<p>%s</p>' % (h[6], T['contact'][i] % CONTACT),
        '</section>'])


def page(p):
    return '\n'.join([
        '<!DOCTYPE html>',
        '<!-- Сгенерировано tools/build_policy.py, руками не править. Черновик: перед публикацией — просмотр владельцем/юристом. -->',
        '<html lang="ru">', '<head>', '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>Matchhold — Политика конфиденциальности / Privacy Policy (%s)</title>' % html.escape(P[p]['name'][1]),
        '<style>', CSS, '</style>', '</head>', '<body>', '<main>',
        '<nav><a href="#ru">Русский</a><a href="#en">English</a></nav>', '',
        section(p, 0), '', section(p, 1), '</main>', '</body>', '</html>', ''])


if __name__ == '__main__':
    for p in P:
        d = os.path.join(OUT, p, 'matchhold', 'policy')
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page(p))
        print('https://games.sarville.online/%s/matchhold/policy -> %s' % (p, d))

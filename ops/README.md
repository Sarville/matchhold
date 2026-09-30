# ops/ — серверная часть VK/OK для Matchhold

Игра на VK Mini Apps / OK отдаётся статикой Caddy, а маленький Node-сервис `vk-payments-matchhold`
(`ops/vk-payments/server.js`, без зависимостей) делает три вещи:

1. **Гейт запуска** (`GET /vk/matchhold`): Caddy `forward_auth` пропускает страницу игры, только если подпись
   launch-параметров валидна (HMAC-SHA256), `vk_ts` свежий (≤ 8 ч; у OK в миллисекундах — учтено) и Referer
   с vk.com / vk.ru / ok.ru / `games.sarville.online` (или отсутствует).
2. **Платежи**: вебхук `POST /vk/matchhold-payments` (`get_item`, `order_status_change`, подпись md5 + секрет)
   и `GET /vk/matchhold-payments/ok` (отдельное подтверждение покупки OK). Пишут в леджер `entitlements.json`
   `{adsDisabled:true}` по ключу `<vk|ok>_<id>` (OK-покупка — `ok_`, VK — `vk_` или `ok_`, если в уведомлении `site=OK`). Клиент читает `GET /vk/matchhold-entitlements` (VK не даёт «мои покупки»). Лимит 60 запросов/мин на пользователя (429).
3. **Облачные сохранения** (`/vk/matchhold-savegames`, GET/POST): один JSON `{ts,data}` на пользователя,
   `SAVEGAMES_DIR/<vk|ok>_<vk_user_id>.json` (id в VK и OK могут совпасть; старые `<id>.json` при старте
   переименовываются в `vk_<id>.json`), лимит 2 МБ (413). Принимается только `{ts:number, data:{slotN|gameOptions: string}}`,
   иначе 400. Не VK Storage (там 4096 байт на ключ). Записи атомарные (tmp + rename), GET ничего не создаёт.

Единственный товар — `disable_ads` (не расходуемый, поэтому `consume` нет).

## Структура

```
ops/vk-payments/server.js        сервис (env: VK_APP_SECRET, DATA_FILE, SAVEGAMES_DIR, PORT, ITEM_PRICE_VK, ITEM_PRICE_OK)
ops/vk-payments/server.test.js   самопроверка: node ops/vk-payments/server.test.js
ops/Caddyfile.matchhold.snippet  блоки для общего Caddyfile
```

На сервере: билд `dist/vk/` → `/opt/games/site/vk/matchhold/`; контейнер `vk-payments-matchhold`
(`node:22-alpine`, `node /server.js`, порт 3000, сеть `games-net`, bind-mount `/data`).

`www/js/lib/vk-bridge.min.js` — vk-bridge 3.0.2 (`window.vkBridge`); `www/js/app/platform/vk.js` подгружает его сам,
если глобала нет, так что в сборку `dist/vk/` нужно просто включить `js/lib/`.

## Цены — сверить руками

Цена «Отключить рекламу» — **150 ₽** на всех площадках. Курс (задан владельцем): 1 голос = 10 ₽, 100 ОК = 125 ₽
(1 ОК = 1,25 ₽), 1 Ян = 1 ₽. Отсюда: `ITEM_PRICE_VK` = 15 голосов, `ITEM_PRICE_OK` = 120 ОК (по умолчанию в `server.js`),
Яндекс — 150 Ян в кабинете, RuStore — 150 ₽. В игре цена показывается на кнопке в валюте площадки (VK — голоса,
OK — ОК, Яндекс/RuStore — ₽): ключи `PRICE_VK/PRICE_OK/PRICE_RUB` в `www/js/app/locale/*.js`, `priceKey` в провайдере.
Менять цену — во всех местах сразу (env сервера, кабинеты, locale). Для OK сервер сверяет `amount` подтверждения с
`ITEM_PRICE_OK` — при рассинхроне покупка отклоняется. Курс сверить с витриной покупок кабинета перед публикацией.

## Проверка

```
node ops/vk-payments/server.test.js
```

## Деплой (выполняет человек, автоматически не запускается)

1. Скачать живой Caddyfile, сделать `diff` с `Caddyfile.matchhold.snippet` и вставить блоки внутрь существующего
   `route { ... }`. Общий файл целиком не перезаписывать — заденет другие игры.
2. Бэкап → `caddy validate` → `caddy reload`.
3. Собрать билд, залить в `/opt/games/site/vk/matchhold/`, запустить контейнер `vk-payments-matchhold` с
   `VK_APP_SECRET` из окружения сервера (значение нигде не хранить в репозитории и не выводить в логи).

## В кабинете VK / OK — вручную

- Создать приложение типа «Встраиваемое приложение → Игра». URL iframe: `https://games.sarville.online/vk/matchhold/`.
- Платежи: callback URL `https://games.sarville.online/vk/matchhold-payments`; в поле для OK — 
  `https://games.sarville.online/vk/matchhold-payments/ok`.
- Товар `disable_ads` (название «Отключить рекламу»), цену выставить по витрине (см. выше).
- Защищённый ключ приложения — только в env сервера `VK_APP_SECRET`.
- Пройти модерацию VK (в т.ч. проверка покупки кнопкой «Тестовый» — суффикс `_test` обрабатывается).

# ops/ — серверная часть VK/OK для Matchhold

Игра на VK Mini Apps / OK отдаётся статикой Caddy, а маленький Node-сервис `vk-payments-matchhold`
(`ops/vk-payments/server.js`, без зависимостей) делает три вещи:

1. **Гейт запуска** (`GET /vk/matchhold`): Caddy `forward_auth` пропускает страницу игры, только если подпись
   launch-параметров валидна (HMAC-SHA256), `vk_ts` свежий (≤ 8 ч; у OK в миллисекундах — учтено) и Referer
   с vk.com / vk.ru / ok.ru / `games.sarville.online` (или отсутствует).
2. **Платежи**: вебхук `POST /vk/matchhold-payments` (`get_item`, `order_status_change`, подпись md5 + секрет)
   и `GET /vk/matchhold-payments/ok` (отдельное подтверждение покупки OK). Пишут в леджер `entitlements.json`
   `{adsDisabled:true}` по `vk_user_id`. Клиент читает `GET /vk/matchhold-entitlements` (VK не даёт «мои покупки»).
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

`ITEM_PRICE_VK` (голоса, по умолчанию 10) и `ITEM_PRICE_OK` (ОКи, по умолчанию 30) — **заглушки**. Голоса и ОКи
не равны рублям и друг другу; курс и допустимые значения смотреть на витрине покупок в кабинете VK/OK и выставить
env перед первой публикацией. Для OK сервер сверяет `amount` подтверждения с `ITEM_PRICE_OK` — при рассинхроне покупка отклоняется.

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

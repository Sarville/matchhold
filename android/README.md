# Matchhold — Android (RuStore)

Capacitor 8 оборачивает статический билд игры (`dist/android`). Покупки — RuStore Pay SDK 10.5.0
(плагин `RuStorePayPlugin`), реклама — Yandex Mobile Ads (`@quenary/capacitor-yandex-ads`).
`applicationId`: `ru.sarville.matchhold` — **после первой загрузки в RuStore не менять.**

## Требования
JDK 21 (`~/jdk21`), Android SDK (`~/Android/Sdk`), Node (для Capacitor CLI), Pillow (для `make_assets.py`).

```bash
export JAVA_HOME=~/jdk21 PATH=~/jdk21/bin:$PATH ANDROID_HOME=~/Android/Sdk
```

## Сборка
```bash
python3 tools/build_platform.py android      # -> dist/android
npm install                                  # один раз
npx cap sync android
cd android
./gradlew assembleDebug                      # app/build/outputs/apk/debug/app-debug.apk
./gradlew bundleRelease                      # app/build/outputs/bundle/release/app-release.aab (нужна подпись)
```
Версию поднимать в `app/build.gradle` (`versionCode` строго растёт с каждой загрузкой, `versionName`).

## До релиза обязательно заменить
1. **`rustoreConsoleAppId`** в `gradle.properties` — сейчас `0`, покупки не заработают. Берётся в RuStore Console →
   приложение → «ID приложения».
2. **ID рекламных блоков** `yandexBannerId` / `yandexInterstitialId` / `yandexRewardedId` (награждаемая реклама: воскрешение/повтор ночи) — сейчас публичные демо-блоки Яндекса
   (`demo-banner-yandex`, `demo-interstitial-yandex`, `demo-rewarded-yandex`): реклама показывается, но **не платит**. Реальные `R-M-…`
   создаются в кабинете РСЯ (partner.yandex.ru) для приложения. Можно задать в `gradle.properties` или на сборке:
   `./gradlew bundleRelease -PyandexBannerId=R-M-... -PyandexInterstitialId=R-M-... -PyandexRewardedId=R-M-...`.
3. Товар в RuStore Console → Монетизация: `disable_ads`, тип **NON_CONSUMABLE** (id должен совпадать с
   `DISABLE_ADS` в `www/js/app/platform/android.js`).

## Подпись
Ключи живут вне репозитория: `~/keys/matchhold/` (инструкция — `~/keys/matchhold/README.md`). Скопируйте
`keystore.properties.example` в `keystore.properties` (в `.gitignore`), впишите пароли. **Без этого файла
`bundleRelease`/`assembleRelease` падают с ошибкой** (не выдают молча неподписанный артефакт); для тестового
неподписанного — `-PallowUnsigned=true`. Проверка: `jarsigner -verify -verbose:summary -certs app-release.aab`.
Никогда не коммитьте `keystore.properties`, `*.jks`, `pepk*` (уже в `android/.gitignore`).

## Что настроено
- `AndroidManifest.xml`: `portrait`, `singleTask`, deeplink-схема `matchholdpay` (возврат из СБП/SberPay),
  `console_app_id_value`/`sdk_pay_scheme_value` для RuStore Pay.
- `MainActivity`: кнопка/жест «Назад» отправляет Escape на `document` (в игре это «назад»: закрыть окно,
  пауза; в главном меню — ничего), приложение случайно не закрывается. Также `proceedIntent` для deeplink оплаты.
- `RuStorePayPlugin`: `getPurchases`, `purchase` (one-step), `acknowledge`, `getConfig` (ID блоков из сборки).
- Провайдер JS — `www/js/app/platform/android.js`; прогресс только в localStorage, «Отключить рекламу» также
  запоминается локально на случай запуска без сети.

## Иконки и сплэш
`python3 android/make_assets.py` — из `www/img/v2/emblem.webp` перегенерирует иконку лаунчера (адаптивная, арт в
центральных 50%), сплэш и `values/ic_launcher_background.xml`, а также `android/store-icon-512.png` (иконка
для магазина; эмблема 300px, на 512 слегка мягкая).

## Проверка на эмуляторе (WSL)
```bash
setsid nohup emulator -avd colorit -no-window -no-audio -no-snapshot -gpu swiftshader_indirect > /tmp/emu.log 2>&1 & disown
adb wait-for-device; until [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = 1 ]; do sleep 3; done
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n ru.sarville.matchhold/.MainActivity
adb logcat -s Capacitor Capacitor/Console chromium
```
На эмуляторе без RuStore/сервисов покупки вернут ошибку — это нормально; проверять оплату нужно на устройстве
с установленным RuStore и тестовым платежом.

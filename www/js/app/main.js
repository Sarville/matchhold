// jquery первым: модули без явной зависимости берут $ из обёртки бандла и используют его при загрузке
define(["jquery", "app/platform", "app/engine", "app/locale/ru", "app/locale/en"], function(_, Platform, Engine, ru, en) {
	var lang;
	try { lang = JSON.parse(localStorage.gameOptions).lang; } catch(e) {}
	if(lang != 'ru' && lang != 'en') lang = /^ru/i.test(navigator.language || '') ? 'ru' : 'en';

	// подсказки загрузочного экрана: inline-скрипт в index.html слушает это событие
	document.dispatchEvent(new CustomEvent('mhtips', { detail: (lang == 'ru' ? ru : en).LOAD_TIPS }));

	// Platform init (SDK, cloud save, language) first, then the game
	Platform.boot(function() {
		Engine.init();
	});
});

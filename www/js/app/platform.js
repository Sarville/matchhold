// Общий слой платформ (Яндекс.Игры / VK+OK / Android RuStore). Платформу выбирает сборка: window.G_PLATFORM.
// Провайдер (app/platform/<name>) возвращает объект:
//   name, init() -> Promise<{lang}>, ready(), load() -> Promise<{ts,data}|null>, save({ts,data}),
//   gameplay(on) (необяз.), showBanner(), hideBanner(), showInterstitial() -> Promise<bool>, showRewarded() -> Promise<bool> (true = награда заслужена), adsPurchased() -> Promise<bool>, buyAdsOff() -> Promise<bool>
// Все методы-промисы не реджектятся. Без G_PLATFORM (dev/web) слой ничего не делает.
define(['app/eventmanager'], function(E) {

	var INIT_TIMEOUT = 8000;
	var SYNC_EVERY = 20000;
	var AD_GRACE = 90000;    // после входа в игру, мс
	var AD_COOLDOWN = 180000; // между интерстишлами, мс

	var PLATFORM = window.G_PLATFORM; // фиксируем при загрузке: правка глобала в консоли не должна отключать проверку рекламы
	var provider = null;
	var adsOff = false;
	var adBusy = false, lastAd = 0, playStart = 0;
	var lastSynced = null;
	var readyDone = false;

	function store(key, value) {
		try {
			if(value === undefined) {
				return localStorage.getItem(key);
			}
			localStorage.setItem(key, value);
		} catch(e) {}
	}

	function snapshot() {
		var data = {};
		try {
			for(var i = 0; i < localStorage.length; i++) {
				var k = localStorage.key(i);
				if(/^slot\d+$/.test(k) || k == 'gameOptions') {
					data[k] = localStorage.getItem(k);
				}
			}
		} catch(e) {}
		return data;
	}

	function hydrate(blob) {
		var old = snapshot();
		for(var k in old) {
			if(!(k in blob.data)) {
				try { localStorage.removeItem(k); } catch(e) {}
			}
		}
		for(var k in blob.data) {
			if(typeof blob.data[k] == 'string' && (/^slot\d+$/.test(k) || k == 'gameOptions')) store(k, blob.data[k]);
		}
		store('mh_ts', String(blob.ts));
	}

	// «новее побеждает» на весь снимок; ponytail: без слияния слотов между устройствами
	function flush() {
		if(!provider) return;
		var data = snapshot(), str = JSON.stringify(data);
		if(str === lastSynced) return;
		lastSynced = str;
		var blob = { ts: Date.now(), data: data };
		store('mh_ts', String(blob.ts));
		provider.save(blob);
	}

	function applyLang(lang) {
		if(!lang) return;
		var o = {};
		try { o = JSON.parse(store('gameOptions')) || {}; } catch(e) {}
		if(!o.lang) {
			o.lang = lang;
			store('gameOptions', JSON.stringify(o));
		}
	}

	function setShopVisible() {
		var ads = document.getElementById('btnAds'), more = document.getElementById('btnMore');
		if(ads) ads.style.display = adsOff ? 'none' : '';
		if(more) more.style.display = 'none';
	}

	function setAdsOff() {
		adsOff = true;
		setShopVisible();
		provider && provider.hideBanner();
	}

	function tryInterstitial() {
		var now = Date.now();
		if(!provider || adsOff || adBusy || !playStart || now - playStart < AD_GRACE || now - lastAd < AD_COOLDOWN) return;
		if(require('app/engine').paused) return;
		var prev = lastAd;
		adBusy = true;
		lastAd = now;
		E.trigger('pause', [true]);
		provider.showInterstitial().then(function(shown) {
			adBusy = false;
			if(!shown) lastAd = prev;
			E.trigger('unpause');
		});
	}

	function gameplay(on) {
		provider && provider.gameplay && provider.gameplay(on);
	}

	function buy() {
		if(!provider || adsOff) return;
		provider.buyAdsOff().then(function(ok) {
			if(ok) {
				setAdsOff();
				require('app/ui').modal({ title: 'REMOVE_ADS', text: 'ADS_REMOVED', buttons: [{ text: 'CLOSE' }] });
			}
		});
	}

	function start(name, done) {
		var finished = false;
		function finish() {
			if(!finished) {
				finished = true;
				done();
			}
		}
		setTimeout(finish, INIT_TIMEOUT);
		require(['app/platform/' + name], function(p) {
			provider = p;
			setShopVisible();
			p.init().then(function(info) {
				return p.load().then(function(blob) {
					if(blob && blob.data && blob.ts > (+store('mh_ts') || 0)) {
						hydrate(blob);
					}
					lastSynced = JSON.stringify(snapshot());
					if(!blob) lastSynced = null;
					applyLang(info && info.lang);
				});
			}).then(function() {
				return p.adsPurchased();
			}).then(function(bought) {
				if(bought) setAdsOff();
			}).then(finish, finish);
		}, finish);
	}

	var Platform = {
		// раз в загрузку страницы: SDK, облачное сохранение, язык; потом done()
		boot: function(done) {
			if(!PLATFORM) return done();
			start(PLATFORM, done);
			setInterval(flush, SYNC_EVERY);
			document.addEventListener('visibilitychange', function() { document.hidden && flush(); });
			window.addEventListener('pagehide', flush);
		},

		// модуль движка: EventManager.init() стирает подписки, поэтому подписываемся при каждом Engine.init
		init: function() {
			if(!provider) return;
			E.bind('gameLoaded', function() { playStart = Date.now(); gameplay(true); });
			E.bind('nightEnd', tryInterstitial);
			E.bind('menuReturn', tryInterstitial);
			E.bind('pause', function() { gameplay(false); });
			E.bind('unpause', function() { gameplay(true); });
		},

		removeAds: buy,

		// реклама за награду (воскрешение / повтор ночи): награда только за реально показанную рекламу.
		// Платформенная сборка без провайдера (офлайн, SDK не загрузился) — нет рекламы, нет награды; в dev без платформы выдаётся сразу
		showRewarded: function() {
			if(!provider) return Promise.resolve(!PLATFORM);
			if(!provider.showRewarded || adBusy) return Promise.resolve(false);
			adBusy = true;
			E.trigger('pause', [true]);
			return provider.showRewarded().then(function(ok) {
				adBusy = false;
				lastAd = Date.now();
				E.trigger('unpause');
				return ok;
			});
		},

		// вызывается, когда титульный экран готов к игре
		ready: function() {
			if(!provider || readyDone) return;
			readyDone = true;
			provider.ready();
			adsOff || provider.showBanner();
		}
	};

	return Platform;
});

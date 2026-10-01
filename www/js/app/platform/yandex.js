// Яндекс.Игры. Контракт провайдера — см. app/platform.js. SDK подключается динамически (/sdk.js отдаёт сам Яндекс).
define(['app/eventmanager'], function(E) {

	var ysdk = null, player = null, payments = null;
	var readyCalled = false, playing = false; // playing: состояние GameplayAPI
	var writing = false, pending = null;

	function noop() {}

	function loadSdk() {
		return new Promise(function(resolve) {
			var s = document.createElement('script');
			s.src = '/sdk.js';
			s.onload = function() { resolve(window.YaGames || null); };
			s.onerror = function() { resolve(null); };
			document.head.appendChild(s);
		});
	}

	function lang(l) {
		return /^(ru|be|kk|uk|uz)/.test(l || '') ? 'ru' : 'en';
	}

	function flushSave() {
		if(writing || !pending || !player) return;
		var blob = pending;
		pending = null;
		writing = true;
		// ponytail: лимит setData ~200 КБ не проверен; слоты — короткие JSON-строки
		player.setData({ mh: JSON.stringify(blob) }, false).catch(noop).then(function() {
			writing = false;
			flushSave();
		});
	}

	return {
		name: 'yandex',
		priceKey: 'PRICE_RUB', // 1 Ян = 1 ₽, показываем рубли


		init: function() {
			return loadSdk().then(function(YaGames) {
				return YaGames && YaGames.init();
			}).then(function(sdk) {
				ysdk = sdk || null;
				if(!ysdk) return { lang: null };
				ysdk.on && ysdk.on('game_api_pause', function() { E.trigger('pause', [true]); });
				ysdk.on && ysdk.on('game_api_resume', function() { E.trigger('unpause'); });
				var p1 = ysdk.getPlayer({ scopes: false }).then(function(p) { player = p; }, noop);
				var p2 = ysdk.getPayments({ signed: false }).then(function(p) { payments = p; }, noop);
				return Promise.all([p1, p2]).then(function() {
					return { lang: lang(ysdk.environment && ysdk.environment.i18n && ysdk.environment.i18n.lang) };
				});
			}).catch(function() { return { lang: null }; });
		},

		canAuth: function() { return !!(ysdk && player); },

		isAuthorized: function() { return !!(player && player.isAuthorized()); },

		auth: function() {
			if(!ysdk) return Promise.resolve(false);
			return ysdk.auth.openAuthDialog().then(function() {
				return ysdk.getPlayer({ scopes: false });
			}).then(function(p) {
				player = p;
				return p.isAuthorized();
			}).catch(function() { return false; });
		},

		gameplay: function(on) {
			if(!ysdk || playing == on) return;
			playing = on;
			try { on ? ysdk.features.GameplayAPI.start() : ysdk.features.GameplayAPI.stop(); } catch(e) {}
		},

		ready: function() {
			if(!ysdk || readyCalled) return;
			readyCalled = true;
			try { ysdk.features.LoadingAPI.ready(); } catch(e) {}
		},

		load: function() {
			if(!player) return Promise.resolve(null);
			return player.getData(['mh']).then(function(d) {
				var blob = d && d.mh && JSON.parse(d.mh);
				return blob && blob.data ? blob : null;
			}).catch(function() { return null; });
		},

		save: function(blob) {
			pending = blob;
			flushSave();
		},

		showBanner: function() {
			try { ysdk && ysdk.adv.showBannerAdv().catch(noop); } catch(e) {}
		},

		hideBanner: function() {
			try { ysdk && ysdk.adv.hideBannerAdv().catch(noop); } catch(e) {}
		},

		showInterstitial: function() {
			if(!ysdk) return Promise.resolve(false);
			return new Promise(function(resolve) {
				var shown = false, done = false;
				function end(v) {
					if(!done) {
						done = true;
						resolve(v);
					}
				}
				try {
					ysdk.adv.showFullscreenAdv({
						callbacks: {
							onOpen: function() { shown = true; },
							onClose: function(wasShown) { end(!!wasShown || shown); },
							onError: function() { end(false); },
							onOffline: function() { end(false); }
						}
					});
				} catch(e) {
					end(false);
				}
			});
		},

		showRewarded: function() {
			if(!ysdk) return Promise.resolve(false);
			return new Promise(function(resolve) {
				var rewarded = false, done = false;
				function end() {
					if(!done) {
						done = true;
						resolve(rewarded);
					}
				}
				try {
					ysdk.adv.showRewardedVideo({
						callbacks: {
							onRewarded: function() { rewarded = true; },
							onClose: end,
							onError: function() { rewarded = false; end(); }
						}
					});
				} catch(e) {
					end();
				}
			});
		},

		adsPurchased: function() {
			if(!payments) return Promise.resolve(false);
			return payments.getPurchases().then(function(list) {
				return (list || []).some(function(p) { return p.productID == 'disable_ads'; });
			}).catch(function() { return false; });
		},

		buyAdsOff: function() {
			if(!payments) return Promise.resolve(false);
			return payments.purchase({ id: 'disable_ads' }).then(function() { return true; }, function() { return false; });
		}
	};
});

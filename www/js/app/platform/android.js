// Android (RuStore): Capacitor-обёртка. Покупки — RuStore Pay SDK (плагин RuStorePay), реклама — Yandex Mobile Ads.
// Контракт провайдера — см. app/platform.js. Прогресс только в localStorage (load() -> null, save() ничего не делает).
// Нативные плагины зовём через Capacitor.nativePromise/addListener из native-bridge.js (бандлера и @capacitor/core нет).
define([], function() {

	var DISABLE_ADS = 'disable_ads'; // NON_CONSUMABLE в RuStore Console
	var ADS_KEY = 'matchhold_ads_disabled'; // офлайн-запас, если список покупок RuStore недоступен
	// Публичные демо-блоки Яндекса: показываются, но не платят. Реальные R-M-… подставляет сборка (android/README.md).
	var DEMO_BANNER = 'demo-banner-yandex', DEMO_INTERSTITIAL = 'demo-interstitial-yandex', DEMO_REWARDED = 'demo-rewarded-yandex';

	var cap = window.Capacitor;
	var bannerId = DEMO_BANNER, interstitialId = DEMO_INTERSTITIAL, rewardedId = DEMO_REWARDED;
	var adsOff = false;
	var adsInit = null, interstitialReady = false, bannerLoaded = false, onDone = null;
	var rewardedReady = false, rewardedLoading = null, rewardedGot = false, rewardedDone = null;

	function pay(method, opts) { return cap.nativePromise('RuStorePay', method, opts || {}); }
	function ads(method, opts) { return cap.nativePromise('YandexAds', method, opts || {}); }
	function on(event, cb) { cap.addListener('YandexAds', event, cb); }

	function isPaid(p) { return p.status == 'PAID' || p.status == 'CONFIRMED'; }

	function storeAdsOff() {
		try { localStorage.setItem(ADS_KEY, adsOff ? '1' : '0'); } catch(e) {}
	}

	function initAds() {
		if(!adsInit) {
			adsInit = ads('setUserConsent', { value: true }).then(function() {
				return ads('initialize');
			}).then(function() {
				on('interstitialAdDismissed', function() { finish(true); });
				on('interstitialAdFailedToShow', function() { finish(false); });
				on('rewardedVideoAdRewarded', function() { rewardedGot = true; });
				on('rewardedVideoAdDismissed', function() { finishRewarded(rewardedGot); });
				on('rewardedVideoAdFailedToShow', function() { finishRewarded(false); });
				loadInterstitial();
				loadRewarded();
			});
			adsInit.catch(function() { adsInit = null; }); // офлайн — следующий вызов попробует снова
		}
		return adsInit;
	}

	function loadInterstitial() {
		interstitialReady = false;
		ads('loadInterstitial', { adUnitId: interstitialId }).then(function() {
			interstitialReady = true;
		}, function() {}); // нет сети/показов — следующий показ попробует снова
	}

	function loadRewarded() {
		if(!rewardedLoading) {
			rewardedReady = false;
			rewardedLoading = ads('loadRewardedVideo', { adUnitId: rewardedId }).then(function() {
				rewardedReady = true;
			}, function() {}).then(function() { rewardedLoading = null; });
		}
		return rewardedLoading;
	}

	function finishRewarded(ok) {
		var d = rewardedDone;
		rewardedDone = null;
		loadRewarded(); // предзагрузка следующего
		d && d(ok);
	}

	function finish(shown) {
		loadInterstitial();
		var d = onDone;
		onDone = null;
		d && d(shown);
	}

	return {
		name: 'android',

		init: function() {
			if(!cap || !cap.nativePromise) return Promise.resolve({ lang: null });
			try { adsOff = localStorage.getItem(ADS_KEY) == '1'; } catch(e) {}
			return pay('getConfig').then(function(c) {
				if(c.bannerId) bannerId = c.bannerId;
				if(c.interstitialId) interstitialId = c.interstitialId;
				if(c.rewardedId) rewardedId = c.rewardedId;
			}).catch(function() {}).then(function() { return { lang: null }; });
		},

		ready: function() {},

		load: function() { return Promise.resolve(null); },
		save: function() {},

		showBanner: function() {
			if(adsOff || !cap) return;
			initAds().then(function() {
				if(bannerLoaded) return;
				// сверху: снизу у игры свои кнопки
				return ads('loadBanner', { adUnitId: bannerId, position: 'top', overlap: false }).then(function() { bannerLoaded = true; });
			}).then(function() {
				return ads('showBanner');
			}).catch(function() {});
		},

		hideBanner: function() {
			if(bannerLoaded) ads('hideBanner').catch(function() {});
		},

		showInterstitial: function() {
			if(adsOff || !cap) return Promise.resolve(false);
			return initAds().then(function() {
				if(!interstitialReady) return false;
				interstitialReady = false;
				return new Promise(function(resolve) {
					onDone = resolve;
					ads('showInterstitial').catch(function() { finish(false); });
				});
			}).catch(function() { return false; });
		},

		// не зависит от adsOff: купленное отключение рекламы не касается рекламы за награду
		showRewarded: function() {
			if(!cap || !cap.nativePromise || rewardedDone) return Promise.resolve(false);
			return initAds().then(function() {
				if(rewardedReady) return true;
				// ponytail: не готово — грузим и ждём до 10 с
				return Promise.race([loadRewarded().then(function() { return rewardedReady; }), new Promise(function(r) { setTimeout(function() { r(false); }, 10000); })]);
			}).then(function(ready) {
				if(!ready) return false;
				rewardedReady = false;
				rewardedGot = false;
				return new Promise(function(resolve) {
					rewardedDone = resolve;
					ads('showRewardedVideo').catch(function() { finishRewarded(false); });
				});
			}).catch(function() { return false; });
		},

		adsPurchased: function() {
			if(!cap || !cap.nativePromise) return Promise.resolve(false);
			return pay('getPurchases').then(function(r) {
				adsOff = r.purchases.some(function(p) { return isPaid(p) && p.productId == DISABLE_ADS; });
				storeAdsOff();
				return adsOff;
			}).catch(function() { return adsOff; }); // офлайн/RuStore недоступен — локальный флаг
		},

		buyAdsOff: function() {
			return pay('purchase', { productId: DISABLE_ADS }).then(function() {
				adsOff = true;
				storeAdsOff();
				return true;
			}).catch(function() { return false; });
		}
	};
});

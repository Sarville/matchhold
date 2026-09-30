// VK Mini Apps + OK (тот же Mini App, vk_client=ok). Контракт провайдера — см. app/platform.js.
// Сервер (ops/vk-payments): /vk/matchhold-entitlements, -savegames; покупки подтверждает вебхук VK/OK.
define([], function() {

	var BRIDGE_SRC = 'js/lib/vk-bridge.min.js';
	var QS = location.search;
	var params = new URLSearchParams(QS);
	var inVk = params.has('vk_user_id');
	var bridge = null;

	function timeout(p, ms) {
		return Promise.race([p, new Promise(function(_, rej) { setTimeout(function() { rej(new Error('timeout')); }, ms); })]);
	}

	function send(method, data) {
		return bridge ? bridge.send(method, data) : Promise.reject(new Error('no bridge'));
	}

	function loadBridge() {
		if(window.vkBridge) return Promise.resolve(window.vkBridge);
		return new Promise(function(resolve) {
			var s = document.createElement('script');
			s.src = BRIDGE_SRC;
			s.onload = function() { resolve(window.vkBridge || null); };
			s.onerror = function() { resolve(null); };
			document.head.appendChild(s);
		});
	}

	function api(path, opts) {
		return fetch('/vk/matchhold-' + path + QS, opts).then(function(r) {
			if(!r.ok) throw new Error(path + ' ' + r.status);
			return r.json();
		});
	}

	function entitlements() {
		return api('entitlements').catch(function() { return null; });
	}

	return {
		name: 'vk',
		priceKey: params.get('vk_client') == 'ok' ? 'PRICE_OK' : 'PRICE_VK', // цена в валюте площадки: голоса / ОКи

		init: function() {
			if(!inVk) return Promise.resolve({ lang: null });
			var lang = params.get('vk_language') == 'en' ? 'en' : 'ru'; // правила VK 3.1.2: язык пользователя, по умолчанию русский
			return loadBridge().then(function(b) {
				bridge = b;
				b && b.subscribe(function(e) {
					// правила VK 2.2.5: при сворачивании глушим звук и ставим паузу (pause глушит аудио)
					if(e.detail && e.detail.type == 'VKWebAppViewHide' && require('app/engine').isStarted()) require('app/eventmanager').trigger('pause');
				});
				return b && timeout(b.send('VKWebAppInit'), 8000);
			}).catch(function() {}).then(function() {
				return { lang: lang };
			});
		},

		ready: function() {},

		load: function() {
			if(!inVk) return Promise.resolve(null);
			return api('savegames').catch(function() { return null; });
		},

		save: function(blob) {
			if(!inVk) return Promise.resolve();
			return api('savegames', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(blob)
			}).then(function() {}, function() {});
		},

		showBanner: function() {
			if(!bridge) return;
			send('VKWebAppCheckBannerAd').then(function(r) {
				if(r && r.result) return send('VKWebAppShowBannerAd', { banner_location: 'top' });
			}).catch(function() {});
		},

		hideBanner: function() {
			if(!bridge) return;
			send('VKWebAppHideBannerAd').catch(function() {});
		},

		// Пауза/звук — на стороне platform.js; тут только сам показ.
		showInterstitial: function() {
			if(!bridge) return Promise.resolve(false);
			return send('VKWebAppShowNativeAds', { ad_format: 'interstitial' }).then(function(r) {
				return !!(r && r.result);
			}, function() { return false; });
		},

		showRewarded: function() {
			if(!bridge) return Promise.resolve(false);
			return send('VKWebAppShowNativeAds', { ad_format: 'reward' }).then(function(r) {
				return !!(r && r.result);
			}, function() { return false; });
		},

		adsPurchased: function() {
			if(!inVk) return Promise.resolve(false);
			return entitlements().then(function(e) { return !!(e && e.adsDisabled); });
		},

		// success от ShowOrderBox приходит после вебхука; сервер запишет покупку в леджер, а adsPurchased подтвердит её при следующем входе.
		buyAdsOff: function() {
			if(!bridge) return Promise.resolve(false);
			var hide = this.hideBanner;
			return send('VKWebAppShowOrderBox', { type: 'item', item: 'disable_ads' }).then(function(r) {
				if(!r || !r.success) return false;
				hide();
				return true;
			}, function() { return false; });
		}
	};
});

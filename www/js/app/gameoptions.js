define(['jquery'], function($) {
	
	var gameOptions = {
		musicVolume: 1,
		effectsVolume: 1,
		casualMode: false,
		lang: /^ru/i.test(navigator.language || '') ? 'ru' : 'en'
	};
	
	var GameOptions = {
		get: function(optionName, defaultValue) {
			return gameOptions[optionName] == null ? defaultValue : gameOptions[optionName];
		},
		
		set: function(optionName, value) {
			gameOptions[optionName] = value;
			if(typeof Storage != 'undefined' && localStorage) {
				localStorage.gameOptions = JSON.stringify(gameOptions);
			}
			return value;
		},
		
		load: function() {
			try {
				var savedOptions = JSON.parse(localStorage.gameOptions);
				if(savedOptions) {
					$.extend(gameOptions, savedOptions);
					if(gameOptions.lang != 'ru' && gameOptions.lang != 'en') {
						gameOptions.lang = /^ru/i.test(navigator.language || '') ? 'ru' : 'en';
					}
				}
			} catch(e) {
				// Nothing
			}
		}
	};
	
	return GameOptions;
});
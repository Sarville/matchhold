define(['app/eventmanager'], function(E) {

	var hidden = null, visibilityChangeEvent = null;
	if (typeof document.hidden !== "undefined") { // Opera 12.10 and Firefox 18 and later support 
		hidden = "hidden";
		visibilityChangeEvent = "visibilitychange";
	} else if (typeof document.mozHidden !== "undefined") {
		hidden = "mozHidden";
		visibilityChangeEvent = "mozvisibilitychange";
	} else if (typeof document.msHidden !== "undefined") {
		hidden = "msHidden";
		visibilityChange = "msvisibilitychange";
	} else if (typeof document.webkitHidden !== "undefined") {
		hidden = "webkitHidden";
		visibilityChangeEvent = "webkitvisibilitychange";
	}
	
	// В игре — пауза (снимается кликом); на титуле/в меню играет только музыка, её просто глушим и возвращаем
	function visibilityChange(visibility) {
		var gone = visibility === false || (visibility == null && document[hidden]);
		if(require('app/engine').isStarted()) {
			gone && E.trigger('pause');
		} else {
			E.trigger(gone ? 'menuMute' : 'menuUnmute');
		}
	}
	
	if(hidden != null && window.addEventListener) {
		// Use the Page Visibility API
		document.addEventListener(visibilityChangeEvent, function() { visibilityChange(null); });
	} else {
		// Use old fashioned onblur/onfocus events
		window.onfocus = function() { visibilityChange(true); };
		window.onblur = function() { visibilityChange(false); };
	}
	
	var Visibility = {
		init: function() {
			// Nothing to do!
		},
		// для платформ (VK ViewHide/ViewRestore): gone=true — приложение свернули
		set: function(gone) {
			visibilityChange(!gone);
		},
		isReady: function() {
			return true;
		}
	};
	return Visibility;
});
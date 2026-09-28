define(function() {
	
	var TextStore = function(locale, onReady) {
		var _this = this;
		require(['app/locale/' + (locale || 'en')], function(l) {
			_this.locale = l;
			onReady && onReady();
		});
	};
	
	TextStore.prototype.get = function(key) {
		return this.locale[key];
	};
	
	TextStore.prototype.isReady = function() {
		return this.locale != null;
	};
	
	return TextStore;
});

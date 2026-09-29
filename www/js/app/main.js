require(["app/platform", "app/engine"], function(Platform, Engine) {
	// Platform init (SDK, cloud save, language) first, then the game
	Platform.boot(function() {
		Engine.init();
	});
});
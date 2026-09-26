define(['app/entity/worldentity'], 
		function(WorldEntity) {
	
	var Gem = function() { };
	Gem.prototype = new WorldEntity({
		className: 'gem',
		spriteName: 'gem',
		animationFrames: 1 // в новом листе один кадр на состояние кристалла (строка = число кристаллов)
	});
	Gem.constructor = Gem;
	
	return Gem;
});
define(function() {

	var CDN_PATH = "";
	var spriteinfo = {
		// Buildings (лист v2: 100x107 на строку; порядок строк: blacksmith 0-7, bricklayer 8-11, sawmill 12-19, shack 20-23, gem 24-27 + tower 28, weaver 29-32)
		blacksmith: ['v2/buildings.webp', 0],
		bricklayer: ['v2/buildings.webp', 856],
		sawmill: ['v2/buildings.webp', 1284],
		shack: ['v2/home.webp', 0],
		tower: ['v2/tower.webp', 0],
		weaver: ['v2/buildings.webp', 3103],

		// Monsters (свой лист на каждого, не общий monsters.png; см. rebranding/03-animation.md п.7.3)
		demon: ['v2/monsters/demon.webp', 0],
		dude: ['v2/hero.webp', 0],
		dudenight: ['v2/hero.webp', 0],
		earthelemental: ['v2/monsters/earthElemental.webp', 0],
		fireelemental: ['v2/monsters/fireElemental.webp', 0],
		harmour: ['v2/monsters/hauntedArmour.webp', 0],
		imp: ['v2/monsters/imp.webp', 0],
		lich: ['v2/monsters/lich.webp', 0],
		lizardman: ['v2/monsters/lizardman.webp', 0],
		rat: ['v2/monsters/rat.webp', 0],
		skeleton: ['v2/monsters/skeleton.webp', 0],
		spider: ['v2/monsters/spider.webp', 0],
		warlock: ['v2/monsters/warlock.webp', 0],
		waterelemental: ['v2/monsters/waterElemental.webp', 0],
		zombie: ['v2/monsters/zombie.webp', 0],

		// Icons
		bucklericon: ['icons', 0],
		buttonicons: ['icons', 60],
		dragoneffects: ['icons', 88],
		fireball: ['icons', 176],
		gem: ['v2/tower.webp', 0],
		heart: ['icons', 279],
		items: ['icons', 335],
		menu: ['icons', 363],
		music: ['icons', 443],
		social: ['icons', 699],
		spells: ['icons', 795],
		star:['icons', 875],
		sun: ['icons', 891],
		swordicon: ['icons', 951],
		treasurechest: ['icons', 1011],

		// Tiles
		tilesday: ['v2/tiles.webp', 0],
		tilesnight: ['v2/tiles.webp', 468],

		// Dragon
		dragon: ['dragonsprite', 0],
		dragonhead: ['dragonsprite', 1640],
		dragonneck: ['dragonsprite', 1670]
	};

	var spritesheets = {};
	function loadSheets() {
		for(var key in spriteinfo) {
			var sheet = spriteinfo[key][0];
			if(typeof spritesheets[sheet] == 'undefined') {
				loadSheet(sheet);
			}
		}
	}

	function loadSheet(sheetName) {
		spritesheets[sheetName] = false;
		var spriteImage = new Image();
		spriteImage.onload = function() {
			spritesheets[sheetName] = true;
		};
		spriteImage.src = CDN_PATH + "img/" + sheetName + (sheetName.indexOf('.') < 0 ? ".png" : "");
	}

	function getInfo(spriteName) {
		return spriteinfo[spriteName] || [null, 0];
	}

	// Preload all the spritesheets
	loadSheets();
	
	return {
		getOffset: function(spriteName) {
			return getInfo(spriteName)[1];
		},
		getFilename: function(spriteName) {
			return getInfo(spriteName)[0];
		},
		isReady: function() {
			for(var sheet in spritesheets) {
				if(!spritesheets[sheet]) {
					return false;
				}
			}
			return true;
		}
	};
});

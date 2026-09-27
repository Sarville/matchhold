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

		// Monsters
		demon: ['monsters', 0],
		dude: ['v2/hero.webp', 0],
		dudenight: ['v2/hero.webp', 0],
		earthelemental: ['monsters', 1434],
		fireelemental: ['monsters', 1952],
		harmour: ['monsters', 2239],
		imp: ['monsters', 2582],
		lich: ['monsters', 3002],
		lizardman: ['monsters', 3542],
		rat: ['monsters', 3787],
		skeleton: ['monsters', 3878],
		spider: ['monsters', 4102],
		warlock: ['monsters', 4368],
		waterelemental: ['monsters', 4627],
		zombie: ['monsters', 4900],

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

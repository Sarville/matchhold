define(['base64', 'app/entity/building', 'app/entity/block', 'app/eventmanager', 'app/gamecontent'], 
		function(Base64, Building, Block, E, Content) {
	
	var loadedSlot = 0;
	var MAX_SAVE = 200000; // символов; реальное сохранение — единицы КБ

	function isNum(n, max) {
		return typeof n == 'number' && isFinite(n) && n >= 0 && n <= max;
	}

	function isObj(o) {
		return o !== null && typeof o == 'object' && !Array.isArray(o);
	}

	// Проверка чужого сохранения (импорт, облако, localStorage). Типы построек/складов берутся из Content, а не из сохранения.
	function validState(st) {
		if(!isObj(st)) return false;
		if(!Array.isArray(st.buildings) || st.buildings.length > 200) return false;
		if(!Array.isArray(st.stores) || st.stores.length > 200) return false;
		var i, k;
		for(i = 0; i < st.buildings.length; i++) {
			var b = st.buildings[i];
			if(!isObj(b) || !isObj(b.options) || !isObj(b.options.type)) return false;
			var bt = Content.getBuildingType(b.options.type.className);
			if(!bt) return false;
			b.options.type = bt;
			if(b.requiredResources != null && !isObj(b.requiredResources)) return false;
			for(k in b.requiredResources) {
				if(!isNum(b.requiredResources[k] + 1e6, 2e6)) return false;
			}
		}
		for(i = 0; i < st.stores.length; i++) {
			var s = st.stores[i];
			if(!isObj(s) || !isObj(s.options) || !isObj(s.options.type) || typeof s.options.type.className != 'string') return false;
			var rt = Content.getResourceType(s.options.type.className);
			if(!rt || !isNum(s._quantity, 1000)) return false;
			s.options.type = rt;
		}
		var nums = ['level', 'xp', 'dayNumber', 'gem', 'mana', 'prestige', 'health'];
		for(i = 0; i < nums.length; i++) {
			if(st[nums[i]] != null && !isNum(st[nums[i]], 1e9)) return false;
		}
		if(st.items != null) {
			if(!isObj(st.items)) return false;
			for(k in st.items) {
				// старые сохранения могут содержать удалённые предметы — выбрасываем, а не сбрасываем весь прогресс
				if(!Content.LootType.hasOwnProperty(k) || !isNum(st.items[k], 3)) delete st.items[k];
			}
		}
		if(st.counts != null) {
			if(!isObj(st.counts)) return false;
			for(k in st.counts) {
				if(!isNum(st.counts[k], 1e12)) delete st.counts[k];
			}
		}
		if(st.prioritizedBuilding != null && typeof st.prioritizedBuilding != 'string') return false;
		return true;
	}

	function parseState(raw) {
		if(typeof raw != 'string' || raw.length > MAX_SAVE) return null;
		var st = JSON.parse(raw);
		return validState(st) ? st : null;
	}

	var GameState = {
		create: function() {
			this.buildings = [];
			this.stores = [];
			this.level = 1;
			this.xp = 0;
			this.dayNumber = 1;
			this.items = {};
			this.gem = 0;
			this.mana = 0;
			this.counts = {};
			this.prestige = 0;
			this.prioritizedBuilding = null;
			this.health = this.maxHealth();
			E.trigger('newGame');
		},
		
		getExportCode: function(slot) {
			try {
				var savedState = localStorage["slot" + slot];
				return savedState ? Base64.encode(savedState) : null;
			} catch(e) {
				return null;
			}
		},
		
		getSlotInfo: function(slot) {
			try {
				var savedState = JSON.parse(localStorage["slot" + slot]);
				if(savedState) {
					return {
						maxHealth: GameState.maxHealth(savedState.level),
						day: savedState.dayNumber,
						prestiged: savedState.prestige > 0
					};
				}
			} catch(e) {
				return 'empty';
			}
		},
		
		load: function(slot) {
			slot = slot || loadedSlot;
			var raw = this.pendingRaw;
			this.pendingRaw = null;
			try {
				var savedState = parseState(raw || localStorage["slot" + slot]);
				if(savedState) {
					this.buildings = [];
					for(var i in savedState.buildings) {
						this.buildings.push(Building.makeBuilding(savedState.buildings[i]));
					}
					this.stores = [];
					for (var i in savedState.stores) {
						this.stores.push(Block.makeBlock(savedState.stores[i]));
					}
					this.items = savedState.items || {};
					this.level = savedState.level;
					this.xp = savedState.xp;
					this.dayNumber = savedState.dayNumber || 1;
					this.gem = savedState.gem || 0;
					this.mana = savedState.mana || 0;
					this.counts = savedState.counts || {};
					this.prestige = savedState.prestige || 0;
					this.health = savedState.health || this.maxHealth();
					this.prioritizedBuilding = savedState.prioritizedBuilding;
				} else {
					this.create(slot);
				}
			} catch(e) {
				this.create(slot);
			}
			loadedSlot = slot;
			return this;
		},
		
		// JSON текущего состояния (то, что пишет save)
		serialize: function() {
			var state = {
				buildings: [],
				stores: [],
				level: this.level,
				xp: this.xp,
				dayNumber: this.dayNumber,
				items: this.items,
				gem: this.gem,
				mana: this.mana,
				counts: this.counts,
				prestige: this.prestige,
				health: this.health,
				prioritizedBuilding: this.prioritizedBuilding
			};
			for(var b in this.buildings) {
				var building = this.buildings[b];
				state.buildings.push(Building.makeBuilding(building));
			}
			for(var s in this.stores) {
				var store = this.stores[s];
				state.stores.push(Block.makeBlock(store));
			}
			return JSON.stringify(state);
		},
		
		save: function() {
			if(typeof Storage != 'undefined' && localStorage) {
				localStorage["slot" + loadedSlot] = this.serialize();
			}
			return this;
		},
		
		import: function(slotNum, importCode) {
			try {
				var raw = Base64.decode(importCode);
				if(!parseState(raw)) return null;
				localStorage["slot" + slotNum] = raw;
			} catch(e) {
				return null;
			}
		},
		
		deleteSlot: function(slotNum) {
			if(typeof Storage != 'undefined' && localStorage) {
				localStorage.removeItem('slot' + slotNum);
			}
		},
		
		doPrestige: function() {
			this.buildings.length = 0;
			this.stores.length = 0;
			this.prestige = this.prestige ? this.prestige + 1 : 1;
			this.save();
		},
		
		savePersistents: function() {
			if(typeof Storage != 'undefined' && localStorage && localStorage["slot" + loadedSlot]) {
				var savedState = JSON.parse(localStorage["slot" + loadedSlot]);
				savedState.counts = this.counts;
				savedState.health = this.health;
				localStorage["slot" + loadedSlot] = JSON.stringify(savedState);
			}
		},
		
		removeBlock: function(block) {
			this.stores.splice(this.stores.indexOf(block), 1);
		},
		
		hasBase: (function() {
			var _hasBase = false;
			return function() {
				return _hasBase || (function() {
					for(var b in GameState.buildings) {
						var building = GameState.buildings[b];
						if(building.options.type.isBase && building.built) {
							return _hasBase = true;
						}
					}
					return false;
				})();
			};
		})(),
		
		hasBuilding: function(type, ignoreObsolete) {
			for(var i in this.buildings) {
				var building = this.buildings[i];
				if(building.options.type.className == type.className && building.built && 
						(!ignoreObsolete || !building.obsolete)) {
					return true;
				}
			}
			return false;
		},
		
		getBuilding: function(type) {
			for(var i in this.buildings) {
				var building = this.buildings[i];
				if(building.options.type.className == type.className) {
					return building;
				}
			}
			return null;
		},
		
		maxHealth: function(lvl) {
			lvl = lvl || this.level;
			return 20 + 10 * lvl;
		},
		
		maxShield: function() {
			var highestMod = 1;
			for(var i in this.buildings) {
				var building = this.buildings[i];
				if(building.options.type.tileMod == 'wood' && 
						building.options.type.tileLevel > highestMod &&
						building.built) {
					highestMod = building.options.type.tileLevel;
				}
			}
			return 3 * highestMod;
		},
		
		maxSword: function() {
			var highestMod = 1;
			for(var i in this.buildings) {
				var building = this.buildings[i];
				if(building.options.type.tileMod == 'stone' && 
						building.options.type.tileLevel > highestMod &&
						building.built) {
					highestMod = building.options.type.tileLevel;
				}
			}
			// 3, 3, 3, 5, 5, 5, 7, 7, 7...
			return 3 + (Math.floor((highestMod - 1) / 3) * 2);
		},
		
		swordDamage: function() {
			var highestMod = 1;
			for(var i in this.buildings) {
				var building = this.buildings[i];
				if(building.options.type.tileMod == 'stone' && 
						building.options.type.tileLevel > highestMod &&
						building.built) {
					highestMod = building.options.type.tileLevel;
				}
			}
			// 1, 2, 3, 3, 4, 5, 5, 6, 7... ( + punch damage )
			return 1 + (highestMod - 1) - Math.floor((highestMod - 1) / 3);
		},
		
		maxMana: function() {
			return 3;
		},
		
		magicEnabled: function() {
			return this.gem >= 4;
		},
		
		count: function(key, num) {
			var value = this.counts[key] || 0;
			value += num;
			this.counts[key] = value;
		},
		
		setIfHigher: function(key, num) {
			if(typeof this.counts == 'undefined') return;
			
			var value = this.counts[key] || 0;
			value = num > value ? num : value;
			this.counts[key] = value;
		}
	};
	
	return GameState;
});

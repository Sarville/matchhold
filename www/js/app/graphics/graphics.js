define(['jquery', 'app/eventmanager', 'app/textStore', 'app/gameoptions',
        'app/graphics/gameboard', 'app/graphics/world', 'app/graphics/resources', 
        'app/graphics/loot', 'app/graphics/magic', 'app/graphics/sprites', 'app/ui', 'app/graphics/ending'], 
		function($, EventManager, TextStore, Options, BoardGraphics, WorldGraphics, ResourceGraphics,
				LootGraphics, MagicGraphics, Sprites, UI, Ending) {
	
	var MAX_HEARTS = 14;
	var HEALTH_PER_HEART = 10;
	// Логический размер сцены (art.css): десктоп 760x795 с боковыми панелями, телефон 600x870 (сердца и опыт на рельсах рамки)
	var MIN_SCREEN_WIDTH = 760, MIN_SCREEN_HEIGHT = 865, PORTRAIT_WIDTH = 600, PORTRAIT_HEIGHT = 940, MAX_SCALE = 1.5; // высота с запасом 50 на полосу меню
	var STAGE_LEVELS = [1, 7, 14, 21]; // этап фона (s1..s4) по уровню героя
	
	var textStore;
	var _ww = null, _wh = null;
	var _bossHealth = null;
	var styleSheet = null;
	var currentScale = null, currentHeight = null;
	var heartInfo = { total: 0, big: 0 };
	var imageLoaded = false;
	var isDragon = false;

	// I hate that I have to do this.
	var fallbackAnimationFrame = function(callback, element) {
		window.setTimeout(callback, 1000 / 60);
	};

	var requestAnimationFrame = (function() {
		return window.requestAnimationFrame ||
			window.webkitRequestAnimationFrame ||
			window.mozRequestAnimationFrame ||
			window.onRequestAnimationFrame ||
			window.msRequestAnimationFrame ||
			fallbackAnimationFrame
		})();
	
	var lastTime = null;
	var animations = {};
	/**
	 * Animations have the following properties:
	 *	speed: number, How many pixels per millisecond
	 *	destination: number, Where to move to
	 *	callback: function, What to do when you get there
	 *	stopShort: function, When to stop early
	 *  entity: object, The entity to animate
	 */
	function doEntityAnimation(timestamp) {
		requestAnimationFrame(doEntityAnimation);
		timestamp = timestamp || Date.now();
		if(!lastTime) {
			lastTime = timestamp;
			return;
		}
		// Easy hack to pause the world
		if(!require('app/engine').paused) {
			var delta = timestamp - lastTime;
			for(var guid in animations) {
				var animation = animations[guid];
				var entity = animation.entity;
				var remaining = animation.destination - entity.p();
				var dir = remaining / Math.abs(remaining);
				var toMove = delta / animation.speed; // speed is actually px/ms for weird legacy reasons
				if(remaining * dir < toMove) {
					toMove = remaining * dir;
				}

				entity.p(entity.p() + (toMove * dir));
				setEntityPosition(entity, entity.p());

				if(entity.p() == animation.destination || (animation.stopShort && animation.stopShort())) {
					delete animations[entity.guid()];
					animation.callback && animation.callback();
				}
			}
		}
		lastTime = timestamp;
	}

	function setEntityPosition(entity, pos) {
		var el = entity.el ? entity.el() : entity;
		var val = 'translateX(' + (pos - (entity.width() / 2)) + 'px)';
		el.css({
			'transform': val,
			'-webkit-transform': val,
			'-moz-transform': val,
			'-ms-transform': val,
			'-o-transform': val
		});
	}

	function handleDrawRequest(requestString, options) {
		var moduleString = requestString.substring(0, requestString.indexOf('.'));
		requestString = requestString.substring(requestString.indexOf('.') + 1);
		
		var module = null;
		switch(moduleString.toLowerCase()) {
			case 'board':
				module = BoardGraphics;
				break;
			case 'world':
				module = WorldGraphics;
				break;
			case 'resource':
				module = ResourceGraphics;
				break;
			case 'loot':
				module = LootGraphics;
				break;
			case 'magic':
				module = MagicGraphics;
				break;
		}
		
		var time = 0;
		if(module != null && module.handleDrawRequest) {
			time = module.handleDrawRequest(requestString, options);
		}
		
		setTimeout(function() {
			EventManager.trigger('graphicsActionComplete');
		}, time);
	}
	
	function changeTiles(tileTypes, classToAdd, classToRemove) {
		var tileClasses = '';
		tileTypes.forEach(function(type) {
			tileClasses += (tileClasses.length > 0 ? ', ' : '') + '.tile.' + type;
		});
		var tiles = $(tileClasses);
		tiles.addClass('hidden');
		setTimeout(function() {
			BoardGraphics.el().removeClass(classToRemove).addClass(classToAdd);
			tiles.removeClass('hidden');
		}, 300);
	}
	
	function gameOver(counts) {
		Graphics.get('body').addClass('bigExplosion');
		setTimeout(function() {
			Ending.play(counts, continueGame, newGamePlus);
		}, 2000);
	}
	
	function continueGame() {
		EventManager.trigger('phaseChange', [false]);
		BoardGraphics.el().removeClass('dragonFight');
		var b = Graphics.get('body');
		setTimeout(function() {
			b.addClass('fadeOut');
		}, 1400);
		setTimeout(function() {
			b.removeClass('bigExplosion fadeOut');
		}, 2800);
	}
	
	function newGamePlus() {
		BoardGraphics.el().removeClass('dragonFight');
		var b = Graphics.get('body');
		b.removeClass('night dragonBg');
		setTimeout(function() {
			b.addClass('fadeOut');
			EventManager.trigger('prestige');
		}, 1400);
		setTimeout(function() {
			b.removeClass('bigExplosion fadeOut');
		}, 2800);
	}
	
	function dropBlock(block, building) {
		block.el().remove();
		Graphics.updateCosts(building);
	}
	
	function getNumHearts(health) {
		var numHearts = Math.ceil(health / HEALTH_PER_HEART);
		var numBigHearts = 0;
		if(numHearts > MAX_HEARTS) {
			numBigHearts = numHearts - MAX_HEARTS;
			numHearts = MAX_HEARTS;
		}
		
		return {
			total: numHearts,
			big: numBigHearts
		};
	}
	
	function slotButton(className, textKey, click) {
		return $('<button type="button">').addClass('rbtn ' + className).attr('title', Graphics.getText(textKey))
			.html(UI.icon(className)).on('click', function() { click(); return false; });
	}
	
	function drawSlot(slotInfo, slotIndex) {
		var empty = slotInfo === 'empty';
		var slot = Graphics.make('saveSlot' + (empty ? ' empty' : '')).data('slotIndex', slotIndex);
		var info = Graphics.make('slotInfo').appendTo(slot);
		var buttons = Graphics.make('slotButtons');
		if(empty) {
			info.append(Graphics.make('slotTitle').text(Graphics.getText('NEWGAME')));
			buttons.append(slotButton('import', 'IMPORT', drawImport.bind(null, slotIndex)));
		} else {
			var day = Graphics.make('slotTitle').text(Graphics.getText('DAY') + ' ' + slotInfo.day);
			if(slotInfo.prestiged) {
				day.prepend(Graphics.make('star'));
			}
			var hearts = Graphics.make('slotHearts');
			var heartInfo = getNumHearts(slotInfo.maxHealth);
			for(var heartNum = 0; heartNum < heartInfo.total; heartNum++) {
				Graphics.make(heartNum < heartInfo.big ? 'bigheart' : 'heart').appendTo(hearts);
			}
			info.append(day).append(hearts);
			buttons.append(slotButton('export', 'EXPORT', drawExport.bind(null, slotIndex)))
				.append(slotButton('delete', 'DELETE', drawDelete.bind(null, slotIndex)));
		}
		slot.append(buttons).on('click', function() {
			require('app/audio/audio').play('Click');
			EventManager.trigger('slotChosen', [slotIndex]);
			$('#loadingScreen').addClass('hidden');
			setTimeout(function() {
				$('#loadingScreen').remove();
			}, 1000);
		});
		
		return slot;
	}
	
	function drawImport(slotIndex) {
		EventManager.trigger('click', ['import']);
		var code = Graphics.make('codeBox', 'textarea').attr('spellcheck', 'false');
		UI.modal({
			title: 'IMPORT', text: 'IMPORT_CODE', body: code,
			buttons: [
				{ text: 'CONFIRM', cls: 'ok', click: function() { EventManager.trigger('importSlot', [slotIndex, code.val()]); } },
				{ text: 'CANCEL' }
			]
		});
	}
	
	function drawExport(slotIndex) {
		EventManager.trigger('click', ['export']);
		var code = Graphics.make('codeBox', 'textarea').attr('readonly', true)
			.text(require('app/gamestate').getExportCode(slotIndex));
		UI.modal({
			title: 'EXPORT', text: 'EXPORT_CODE', body: code,
			buttons: [
				{ text: 'COPY', cls: 'ok', click: function() {
					code.select();
					try { document.execCommand('copy'); } catch(e) {}
					$(this).text(Graphics.getText('COPIED'));
					return false;
				} },
				{ text: 'CLOSE' }
			]
		});
	}
	
	function drawDelete(slotIndex) {
		EventManager.trigger('click', ['delete']);
		UI.modal({
			title: 'ARE_YOU_SURE', text: 'DELETE_TEXT',
			buttons: [
				{ text: 'DELETE', cls: 'danger', click: function() {
					EventManager.trigger('deleteSlot', [slotIndex]);
					Graphics.replaceSlot(slotIndex, 'empty');
				} },
				{ text: 'CANCEL' }
			]
		});
	}
	
	var scaleSheet = null;
	function scaleToViewport() {
		var mobile = require('app/gameboard').options.mobile;
		var widthScale = document.documentElement.clientWidth / (mobile ? PORTRAIT_WIDTH : MIN_SCREEN_WIDTH),
			heightScale = document.documentElement.clientHeight / (mobile ? PORTRAIT_HEIGHT : MIN_SCREEN_HEIGHT);
		var minScale = Math.min(MAX_SCALE, widthScale, heightScale);
		var sizeKey = document.documentElement.clientHeight;

		if(!scaleSheet) {
			scaleSheet = newStylesheet();
		}

		if(minScale != currentScale || sizeKey != currentHeight) {
			currentHeight = sizeKey;
			currentScale = minScale;
			while(scaleSheet.cssRules.length > 0) {
				scaleSheet.deleteRule(0);
			}
			var rule = function(scale) {
				return 'transform-origin: 50% 0 0;' +
					'-webkit-transform-origin: 50% 0 0;' +
					'transform: scale(' + scale +');' +
					'-webkit-transform: scale(' + scale +');';
			};
			// сцена по центру экрана по вертикали (фон виден выше и ниже)
			var top = Math.max(0, (document.documentElement.clientHeight - (mobile ? PORTRAIT_HEIGHT - 37.5 : MIN_SCREEN_HEIGHT - 37.5) * minScale) / 2); // нижней полосы меню больше нет: доска сдвинута вниз на 18,75 (было 25)
			Graphics.addStyleRule('#gameContainer', rule(minScale) + 'top: ' + Math.round(top) + 'px;', scaleSheet);
		}
	}
	
	function initStylesheet() {
		var style = $('#styleSheet');
		if(style.length > 0) {
			$(style).remove();
		}
		styleSheet = newStylesheet('styleSheet');
	}
	
	function newStylesheet(id){
		style = document.createElement('style');
		if(id) {
			style.id = id;
		}
		style.appendChild(document.createTextNode("")); // Stupid Webkit
		document.head.appendChild(style);
		return style.sheet;
	}

	function activateHyperspace() {
		$('body').addClass('hyperspace');
		setTimeout(function() {
			$('body').removeClass('hyperspace');
		}, 1000);
	}

	function setPaused(p) {
		$('body').toggleClass('paused', p);
	}

	var Graphics = {
		init: function(opts) {
			loaded = false;
			isDragon = false;
			_bossHealth = null
			$('body').removeClass('night dragonBg').toggleClass('ios', opts.ios);

			// iOS doesn't give enough priority to requestAnimationFrame
			// CSS animations totally lock out the animation loop
			// I hate you, Apple. I hope you know this.
			if(opts.ios) {
				requestAnimationFrame = fallbackAnimationFrame;
			}
			
			textStore = new TextStore(Options.get('lang'), UI.applyLang);
			
			initStylesheet();
			scaleToViewport();
			$(window).off('resize').on('resize', scaleToViewport);
			
			EventManager.bind('draw', handleDrawRequest);
			
			EventManager.bind('pause', setPaused.bind(this, true));
			EventManager.bind('unpause', setPaused.bind(this, false));
			EventManager.bind('monsterKilled', this.monsterKilled);
			EventManager.bind('newEntity', this.addToWorld);
			EventManager.bind('removeEntity', this.removeFromWorld);
			EventManager.bind('healthChanged', this.updateHealthBar);
			EventManager.bind('dayBreak', this.handleDayBreak);
			EventManager.bind('gameOver', gameOver);
			EventManager.bind('blockDown', dropBlock);
			EventManager.bind('keySequenceComplete', activateHyperspace);
			
			BoardGraphics.init();
			WorldGraphics.init();
			ResourceGraphics.init();
			LootGraphics.init();
			MagicGraphics.init();

			requestAnimationFrame(doEntityAnimation);
		},
		
		isScaled: function() {
			return currentScale != null && currentScale != 1;
		},
		
		isReady: function() {
			return Sprites.isReady() && textStore && textStore.isReady();
		},
		
		getText: function(key) {
			return textStore.get(key);
		},
		
		setLocale: function(lang, cb) {
			textStore = new TextStore(lang, cb);
		},
		
		attachHandler: function(moduleName, event, element, handler) {
			var module = require('app/graphics/' + moduleName.toLowerCase());
			module.attachHandler(event, element, handler);
		},
		
		get: function(selector, context, returnEmpty) {
			var ret = context ? context.find(selector) : $(selector);
			if(returnEmpty || ret.length > 0) {
				return ret;
			}
			return null;
		},
		
		addStyleRule: function(selector, rules, sheet) {
			sheet = sheet || styleSheet;
			if(sheet.addRule) {
				// Useless goddamn IE non-standard API. Rabble rabble.
				var length = sheet.cssRules.length;
				sheet.addRule(selector, rules);
				return length;
			} else {
				return sheet.insertRule(selector + '{' + rules + '}', 0);
			}
		},

		removeStyleRule: function(index) {
			styleSheet.deleteRule(index);
		},
		
		remove: function(thing) {
			var el = thing.el ? thing.el() : thing;
			thing.remove();
		},
		
		createResourceBar: function(resource, number) {
			var el = $('<li>').addClass('resourceBar').addClass(resource);
			$('<div>').addClass('resourceBar-inner').appendTo(el);
			return el;
		},
		
		make: function(className, tagName) {
			tagName = tagName || 'div';
			return $('<' + tagName + '>').addClass(className);
		},
		
		addToWorld: function(entity) {
			if(entity.el == null) {
				WorldGraphics.add(entity);
			} else {
				var g = require('app/graphics/graphics');
				WorldGraphics.add(entity.el());
				if(entity.p) {
					g.setPosition(entity, entity.p());
				}
				g.updateSprite(entity);
			}
		},
		
		removeFromWorld: function(entity) {
			WorldGraphics.remove(entity.el ? entity.el() : entity);
		},
		
		worldWidth: function() {
			if(_ww == null) {
				_ww = $('.world').width();
			}
			return _ww;
		},
		
		worldHeight: function() {
			if(_wh == null) {
				_wh = $('.world').height();
			}
			return _wh;
		},
		
		addToGame: function(entity) {
			$('#gameContainer').append(entity.el ? entity.el() : entity);
		},
		
		addToBoard: function(entity) {
			$('.gameBoard').append(entity.el ? entity.el() : entity);
		},
		
		hide: function(entity) {
			(entity.el ? entity.el() : entity).addClass('hidden');
		},
		
		show: function(entity) {
			(entity.el ? entity.el() : entity).removeClass('hidden');
		},
		
		addTilesToContainer: function(entities) {
			var elements = document.createDocumentFragment();
			for(var e in entities) {
				elements.appendChild(entities[e].el()[0]);
			}
			document.getElementById('tileContainer').appendChild(elements);
		},
		
		addMonster: function(monster, side) {
			var el = monster.el();
			monster.p(side == 'left' ? -el.width() : Graphics.worldWidth() + el.width());
			monster.animation(monster.getAnimation(side == "right" ? "left" : "right"));
			setEntityPosition(monster, monster.p());
			el.appendTo('.world');
		},
		
		moveCelestial: function(entity) {
			var el = entity.el();
			var pos = entity.p();
			var height = (Math.abs(pos - Graphics.worldWidth() / 2) / (Graphics.worldWidth() / 2)) * 8;   // амплитуда дуги (была 30): подняли траекторию, реже пересекается со зданиями
			var left = Math.max(0, pos - (el.width() / 2)),
				top = Math.floor(height);
			el.css({
				'transform': 'translate3d(' + left + 'px, ' + top + 'px, 0)',
				'-webkit-transform': 'translate3d(' + left + 'px, ' + top + 'px, 0)',
				'-moz-transform': 'translate3d(' + left + 'px, ' + top + 'px, 0)',
				'-ms-transform': 'translate3d(' + left + 'px, ' + top + 'px, 0)',
				'-o-transform': 'translate3d(' + left + 'px, ' + top + 'px, 0)'
			});
		},
		
		setNight: function(night) {
			if(night) {
				$('body').addClass('night');
			} else {
				$('body').removeClass('night');
			}
		},
		
		phaseTransition: function(celestial, callback) {
			var left = Math.max(0, celestial.p() - (celestial.el().width() / 2));
			celestial.el().css({
				'transform': 'translate3d(' + left + 'px, ' + (Graphics.worldHeight() + 10) + 'px, 0)',
				'-webkit-transform': 'translate3d(' + left + 'px, ' + (Graphics.worldHeight() + 10) + 'px, 0)',
				'-moz-transform': 'translate3d(' + left + 'px, ' + (Graphics.worldHeight() + 10) + 'px, 0)',
				'-ms-transform': 'translate3d(' + left + 'px, ' + (Graphics.worldHeight() + 10) + 'px, 0)',
				'-o-transform': 'translate3d(' + left + 'px, ' + (Graphics.worldHeight() + 10) + 'px, 0)'
			});
			$('body').toggleClass('night');
			var _g = this;
			setTimeout(function() {
				if($('body').hasClass('night')) {
					celestial.animation(1);
				} else {
					celestial.animation(0);
				}
				celestial.el().addClass('noTransition');
				celestial.el().css({
					'transform': 'translate3d(0px, ' + (Graphics.worldHeight() + 10) + 'px, 0)',
					'-webkit-transform': 'translate3d(0px, ' + (Graphics.worldHeight() + 10) + 'px, 0)',
					'-moz-transform': 'translate3d(0px, ' + (Graphics.worldHeight() + 10) + 'px, 0)',
					'-ms-transform': 'translate3d(0px, ' + (Graphics.worldHeight() + 10) + 'px, 0)',
					'-o-transform': 'translate3d(0px, ' + (Graphics.worldHeight() + 10) + 'px, 0)'
				});
				
				setTimeout(function() {
					celestial.el().removeClass('noTransition');
					_g.raiseCelestial(celestial);
					if(callback != null) {
						callback();
					}
				}, 500);
			}, 900);
		},
		
		raiseCelestial: function(celestial) {
			celestial.p(15);
			this.moveCelestial(celestial);
		},
		
		updateCosts: function(building) {
			var show = false;
			for(var r in building.requiredResources) {
				var total = building.options.type.cost[r];
				var has = total - building.requiredResources[r];
				if(has > 0) show = true;
				building.el().find('.resourceBar.' + r + ' .resourceBar-inner').css('width', (has / total * 100) + '%');
			}
			if(show) {
				building.el().find('.resourceBars').addClass('show');
				var replaces = building.getReplaces(require('app/gamestate'));
				if(replaces) {
					replaces.el().data('upgrade', building);
					Graphics.markUpgrading(replaces, true, Object.keys(building.options.type.cost).length);
				}
			}
		},
		
		updateSprite: function(entity) {
			var el = entity.el();
			var spriteRow = (entity.tempAnimation == null ? entity.animationRow : entity.tempAnimation) || 0;
			Graphics.updateSpritePos(el, entity.frame * entity.width(), spriteRow * entity.height() + Sprites.getOffset(entity.options.spriteName));
			var nightSprite = $('.animationLayer', el);
			if(nightSprite) {
				Graphics.updateSpritePos(nightSprite, entity.frame * entity.width(), spriteRow * entity.height() + Sprites.getOffset(entity.options.nightSpriteName));
			}
			if(entity.stepFunction) {
				entity.stepFunction(entity.frame);
			}
		},
		
		updateSpritePos: function(el, x, y) {
			el.css('background-position', -(x) + "px " + -(y) + 'px');
		},
		
		setPosition: function(entity, pos) {
			// Don't spawn chests off-screen
			if(entity.lootable && pos <= 20) {
				pos = 20;
				entity.p(pos);
			}
			if(entity.lootable && pos >= this.worldWidth() - 20) {
				pos = this.worldWidth() - 20;
				entity.p(pos);
			}
			setEntityPosition(entity, pos);
		},
		
		selectTile: function(tile) {
			tile.el().addClass('selected');
		},
		
		deselectTile: function(tile) {
			tile.el().removeClass('selected');
		},

		animateMove: function(entity, pos, callback, stopShort, speedOverride) {
			var el = entity.el();
			animations[entity.guid()] = {
				speed: speedOverride || entity.speed(),
				destination: pos,
				callback: callback,
				stopShort: stopShort,
				entity: entity
			};
		},
		
		markUpgrading: function(building, upgrading, numTypes) {
			if(upgrading) {
				building.el().addClass('upgrading up' + (numTypes || 1));
			} else {
				building.el().removeClass('upgrading');
			}
		},
		
		raiseBuilding: function(building, callback) {
			if(building.options.type.isBase) {
				$('.resources').addClass('hidden');
			}
			var el = building.el();
			var replaces = building.getReplaces(require('app/gamestate'));
			if(replaces) {
				Graphics.markUpgrading(replaces, false);   // иначе .upgrading.upN (margin-bottom +) специфичнее .sunk (margin-bottom -) и старое здание не уезжает под землю, а зависает
				replaces.el().addClass('sunk');
			}
			$('.resourceBars', el).addClass('sunk');
			el.animate({
				'bottom': 0
			}, {
				duration: 5000,
				easing: 'linear',
				complete: function() {
					if(building.options.type.isBase) {
						$('.resources').removeClass('hidden');
					}
					el.find('.resourceBars').remove();
					if(building.options.type.tileMod) {
						changeTiles(
							[building.options.type.tileMod], 
							building.options.type.tileMod + building.options.type.tileLevel,
							building.options.type.tileMod + (building.options.type.tileLevel - 1)
						);
					}
					callback(building);
				}
			});
		},
		
		sinkBuilding: function(building) {
			var el = building.el();
			$('.resourceBars', el).removeClass('sunk');
			el.stop().css('bottom', '-' + el.height() + 'px');
			var replaces = building.getReplaces(require('app/gamestate'));
			if(replaces) {
				replaces.el().removeClass('sunk');
			}
		},
		
		pickUpBlock: function(block) {
			block.el().appendTo('.heldBlock');
		},
		
		updateBlock: function(block) {
			$('div', block.el()).width((block.quantity() / block.max * 100) + '%');
		},
		
		getStatusContainer: function() {
			var healthContainer = $('.statusContainer');
			if(healthContainer.length == 0) {
				healthContainer =  $('<div>').addClass('statusContainer')
					.append($('<div>').addClass('vine day'), $('<div>').addClass('vine night'))
					.append($('<div>').addClass('hearts')).appendTo('.gameBoard');
			}
			return healthContainer;
		},
		
		updateExperience: function(xp, toLevel) {
			var xpBar = $('.xpBar');
			if(xpBar.length == 0) {
				xpBar = $('<div>').addClass('xpBar')
					.addClass('hidden').append($('<div>').addClass('mask')
						.append($('<div>').addClass('fill').addClass('hidden'))).appendTo('.gameBoard');
			}
			xpBar.find('.fill').css('height', (xp / toLevel * 100) + "%");
			setTimeout(function() {
				$('.xpBar, .fill').removeClass('hidden');
			}, 100);
			Graphics.updateSigns();
		},
		
		// Этап фона по уровню героя и числа на столбиках (слева день, справа уровень)
		updateSigns: function(dayNumber) {
			var State = require('app/gamestate');
			var stage = 1;
			STAGE_LEVELS.forEach(function(level, i) {
				if(State.level >= level) {
					stage = i + 1;
				}
			});
			var body = $('body');
			for(var i = 1; i <= STAGE_LEVELS.length; i++) {
				body.toggleClass('stage' + i, i == stage);
			}
			var setNum = function(sign, value) {
				var val = $('.sign.' + sign + ' .val');
				if(val.length > 0 && val.text() != String(value)) {
					var first = val.text() == '';
					val.text(value);
					if(!first) {
						var num = val.parent().removeClass('roll');
						num.css('left'); // перезапуск анимации
						num.addClass('roll');
						if(sign == 'right') {
							var s = $('.sign.right').removeClass('swing');
							s.css('left');
							s.addClass('swing');
						}
					}
				}
			};
			setNum('right', State.level);
			setNum('left', dayNumber || State.dayNumber);
		},
		
		numHearts: function() {
			return heartInfo.total;
		},
		
		updateHealth: function(health, maxHealth) {

			heartInfo = getNumHearts(maxHealth);
			
			var statusContainer = $('.hearts', this.getStatusContainer());
			for(var i = 0, n = heartInfo.total - statusContainer.children().length; i < n; i++) {
				$('<div>').addClass('heart').addClass('prepop').append($('<div>')
						.addClass('mask')).append($('<div>').addClass('mask')
						.addClass('nightSprite')).append($('<div>')
						.addClass('bar')).appendTo(statusContainer);
			}
			for(var i = heartInfo.total; i > 0; i--) {
				var heart = $(statusContainer.children()[i - 1]);
				var heartHealth = HEALTH_PER_HEART;
				if(i <= heartInfo.big) {
					heartHealth *= 2;
					heart.removeClass('heart').addClass('bigheart');
				}
				if(health >= heartHealth) {
					heart.removeClass('empty');
					$('.bar', heart).css('width', '100%');
					health -= heartHealth;
				} else if(health > 0) {
					heart.removeClass('empty');
					$('.bar', heart).css('width', (health / heartHealth * 100) + '%');
					health = 0;
				} else {
					heart.addClass('empty');
					$('.bar', heart).css('width', '0%');
				}
			}
			$('.prepop', statusContainer).each(function(idx, heartEl) {
				setTimeout(function() {
					$(heartEl).detach().appendTo(statusContainer).removeClass('prepop');
				}, idx * 100);
			});
		},
		
		updateShield: function(shield, maxShield) {
			var container = this.getStatusContainer();
			var el = $('.shield', container);
			if(el.length == 0) {
				el = $('<div>').addClass('shield').addClass('prepop')
					.append($('<div>')).insertAfter('.hearts', container);
			}
			if(shield > 0) {
				if(el.hasClass('prepop')) {
					setTimeout(function() {
						el.detach().insertAfter('.hearts', container).removeClass('prepop');
					}, 100);
				}
				$('div', el).width((shield / maxShield * 100) + "%");
			} else {
				$('div', el).width("0%");
				el.addClass('hidden');
				setTimeout(function() {
					el.addClass('prepop').removeClass('hidden');
				}, 300);
			}
		},
		
		updateSword: function(sword, maxSword) {
			var container = this.getStatusContainer();
			var el = $('.sword', container);
			if(el.length == 0) {
				el = $('<div>').addClass('sword').addClass('prepop')
					.append($('<div>')).insertAfter('.hearts', container);
			}
			if(sword > 0) {
				if(el.hasClass('prepop')) {
					setTimeout(function() {
						el.detach().insertAfter('.hearts', container).removeClass('prepop');
					}, 100);
				}
				$('div', el).width((sword / maxSword * 100) + "%");
			} else {
				$('div', el).width("0%");
				el.addClass('hidden');
				setTimeout(function() {
					el.addClass('prepop').removeClass('hidden');
				}, 300);
			}
		},
		
		stop: function(entity) {
			delete animations[entity.guid()];
		},
		
		fadeOut: function(callback) {
			$('.gameBoard').addClass('hidden');
			if(callback) {
				setTimeout(callback, 1000);
			}
		},
		
		notifySave: function() {
			$('.saveSpinner').addClass('active');
			setTimeout(function(){
				$('.saveSpinner').removeClass('active');
			}, 1500);
		},
		
		fireArrow: function(arrowEntity, callback) {
			var start = arrowEntity.options.fireFrom,
				end = arrowEntity.options.fireTo;
			var dist = end - start;
			var ARROW_TIME = 1000;
			var arrow = arrowEntity.el();
			arrow.addClass(dist > 0 ? 'right' : 'left');
			arrow.attr('style', 
				'transform: translateX(' + start + 'px);' +
				'-webkit-transform: translateX(' + start + 'px);' +
				'-moz-transform: translateX(' + start + 'px);' +
				'-ms-transform: translateX(' + start + 'px);' +
				'-o-transform: translateX(' + start + 'px);'
			);
			$('.world').append(arrow);
			
			arrow.css('left'); // Force a redraw before animation
			
			// Move arrow to top of arc
			arrow.attr('style', 
				'transform: translateX(' + (start + dist/2) + 'px);' +
				'-webkit-transform: translateX(' + (start + dist/2) + 'px);' + 
				'-moz-transform: translateX(' + (start + dist/2) + 'px);' + 
				'-ms-transform: translateX(' + (start + dist/2) + 'px);' + 
				'-o-transform: translateX(' + (start + dist/2) + 'px);'
			);
			arrow.addClass('top');
			
			// Move arrow to end of arc
			setTimeout(function() {
				arrow.attr('style', 
					'transform: translateX(' + (start + dist) + 'px);' +
					'-webkit-transform: translateX(' + (start + dist) + 'px);' +
					'-moz-transform: translateX(' + (start + dist) + 'px);' +
					'-ms-transform: translateX(' + (start + dist) + 'px);' +
					'-o-transform: translateX(' + (start + dist) + 'px);'
				);
				arrow.removeClass('top').addClass('bottom');
				setTimeout(function() {
					// Remove arrow
					arrow.remove();
					if(callback) {
						callback(arrow);
					}
				}, ARROW_TIME / 2);
			}, ARROW_TIME / 2);
			
			return arrowEntity;
		},
		
		levelUp: function(dude) {
			var p = dude.p();
			var effect = $('<div>').addClass('levelEffect').css('left', (p - 1) + 'px').appendTo('.world');
			effect.css('left'); // force redraw before animation
			effect.css('height', '100%');
			setTimeout(function() {
				effect.css({
					'width': '100%',
					'left': '0px',
					'opacity': 0
				});
			}, 500);
			setTimeout(function() {
				effect.remove();
			}, 1000);
		},
		
		updateHealthBar: function(entity) {
			if(entity.isBoss) {
				Graphics.setBossHealth(entity.hp(), entity.getMaxHealth());
			} else {
				var bar = entity.el().find('.healthBar div');
				if(bar.length > 0) {
					var healthPercent = Math.floor(entity.hp() / entity.getMaxHealth() * 100);
					bar.css('width', healthPercent + '%');
				}
			}
		},
		
		handleDayBreak: function(dayNumber) {
			Graphics.updateSigns(dayNumber);
			var txt = Graphics.getText('DAY');
			var notifier;
			if(isDragon) {
				changeTiles(['clay', 'cloth', 'grain'], '', 'dragonFight');
				$('body').removeClass('dragonBg');
				isDragon = false;
				Graphics.setBossHealth(0, 0);
			}
			setTimeout(function() {
				notifier = $('<div>').addClass('dayNotifier').text(txt + " " + dayNumber).appendTo('.world');
			}, 1400);
			setTimeout(function() {
				$('.monster, .treasureChest').remove();
				notifier.addClass('hidden');
			}, 3000);
			setTimeout(function() {
				notifier.remove();
			}, 3500);
		},
		
		monsterKilled: function(monster) {
			monster.el().find('.healthBar').addClass('hidden');
		},
		
		enablePlayButton: function() {
			$('#loadingScreen').addClass('ready');
			Graphics.drawSaveSlots();
		},
		
		setBossHealth: function(hp, max) {
			if(_bossHealth == null) {
				_bossHealth = Graphics.make('bossHealth noshow').append(Graphics.make());
				WorldGraphics.add(_bossHealth)
				_bossHealth.css('left');
				_bossHealth.removeClass('noshow');
			}
			
			_bossHealth.find('div').css('width', (hp / max * 100) + '%');
			
			if(hp <= 0) {
				_bossHealth.addClass('noshow');
				setTimeout(function() {
					_bossHealth.remove();
					_bossHealth = null;
				}, 1000);
			}
		},
		
		landDragon: function(dragon, cb) {
			isDragon = true;
			dragon.setPosture('idle');
			dragon.el().addClass('flying');
			dragon.p(dragon.options.flip ? 50 : this.worldWidth() - 50);
			dragon.animation(1, true, function(frame) {
				if(frame == 2) {
					EventManager.trigger('flap');
				}
			});
			dragon.setNeckMount({ x: 50, y: 47 });
			this.addToWorld(dragon);
			dragon.el().css('left'); // force redraw
			dragon.el().removeClass('flying');
			var tiltClass = dragon.options.flip ? 'flipTilted' : 'tilted';
			setTimeout(function() {
				EventManager.trigger('landDragon');
				dragon.animation(0);
				dragon.animationOnce(2, function(frame) {
					dragon.setNeckMount((function() {
						switch(frame) {
							case 0:
								return { x: 50, y: 47 };
							case 1:
								return { x: 30, y: 75 };
							case 2:
								return { x: 20, y: 105 };
							case 3:
								return null;
						}
					})());
				});
				dragon.setPosture('idle', 500);
				BoardGraphics.el().addClass(tiltClass);
				changeTiles(['clay', 'cloth', 'grain'], 'dragonFight', '');
				$('body').addClass('dragonBg');
			}, 1000);
			setTimeout(function() {
				Graphics.setBossHealth(dragon.hp(), dragon.getMaxHealth());
				BoardGraphics.el().removeClass(tiltClass);
				dragon.setPosture('windup', 500);
			}, 1500);
			setTimeout(function() { EventManager.trigger('roar'); dragon.setPosture('roar', 500); }, 2000);
			setTimeout(function() { BoardGraphics.el().addClass('shaking'); }, 2500);
			setTimeout(function() { BoardGraphics.el().removeClass('shaking'); dragon.setPosture('idle', 500); }, 3500);
			if(cb) {
				setTimeout(cb, 4000);
			}
		},
		
		drawSaveSlots: function() {
			var saveSlots = $('.saveSlots').empty();
			for(var i = 0; i < 3; i++) {
				var slotInfo = require('app/gamestate').getSlotInfo(i);
				var slot = drawSlot(slotInfo, i);
				saveSlots.append(slot);
			}
		},
		
		replaceSlot: function(slotIndex, slotInfo) {
			var newSlot = drawSlot(slotInfo, slotIndex);
			var oldSlot = Graphics.get('.saveSlot:nth-child(' + (slotIndex + 1) + ')');
			oldSlot.before(newSlot);
			oldSlot.remove();
		},
		
		drawSlot: drawSlot
	};
	
	return Graphics;
});

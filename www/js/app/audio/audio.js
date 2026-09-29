define(['app/eventmanager', 'app/audio/webaudioprovider', 'app/audio/htmlaudioprovider', 'app/audio/htmlwebaudioprovider'], 
		function(E, WebAudioProvider, HtmlAudioProvider, HtmlWebAudioProvider) {
	
	var MUSIC_TIMEOUT = 30000;
	
	var toLoad = 0;
	var format = null;
	var provider = null;
	var playingMusic = false;
	var longloadTimer = false;
	var playingBossMusic = false;
	var playingEnding = false;
	var playingMenu = false;
	var endingFrom = null;
	var noMusic = false;
	var CDN_PATH = "";
	
	var sounds = {
		DayMusic: {
			file: 'theme-day',
			parts: 5,
			music: true,
			silentIf: function() {
				return require('app/engine').isNight();
			},
			required: true
		},
		NightMusic: {
			file: 'theme-night',
			parts: 5,
			music: true,
			silentIf: function() {
				return !require('app/engine').isNight();
			}
		},
		MenuMusic: {
			file: 'theme-menu',
			music: true,
			onLatePlay: function() {
				!playingMenu && GameAudio.stop('MenuMusic');
			}
		},
		BossMusic: {
			file: 'theme-boss',
			music: true,
			noPlay: true
		},
		EndingMusic: {
			file: 'theme-ending',
			music: true,
			lazy: true,
			silentIf: function() {
				return true;
			},
			onLatePlay: function() {
				playingEnding && crossFade(endingFrom, 'EndingMusic', 1500);
			}
		},
		Click: {
			file: 'click'
		},
		TileClick: {
			file: 'tileclick'
		},
		Match: {
			file: 'match-test'
		},
		Blunt: {
			file: 'blunt'
		},
		Slash: {
			file: 'slash'
		},
		ShieldHit: {
			file: 'shieldhit'
		},
		MonsterHit: {
			file: 'monsterhit'
		},
		ArrowHit: {
			file: 'arrowhit'
		},
		BiteHit: {
			file: 'bite'
		},
		BlockUp: {
			file: 'blockup'
		},
		BlockDown: {
			file: 'blockdown'
		},
		Die: {
			file: 'die'
		},
		Shoot: {
			file: 'shoot'
		},
		Open: {
			file: 'open'
		},
		Heal: {
			file: 'heal'
		},
		Bomb: {
			file: 'bomb'
		},
		Equip: {
			file: 'equip'
		},
		Teleport: {
			file: 'teleport'
		},
		TileExplode: {
			file: 'tilexplode'
		},
		Wing: {
			file: 'wing'
		},
		Haste: {
			file: 'haste'
		},
		RefreshBoard: {
			file: 'reset'
		},
		PhaseChange: {
			file: 'phasechange'
		},
		FreezeTime: {
			file: 'freeze'
		},
		LevelUp: {
			file: 'levelup'
		},
		DragonLand: {
			file: 'land'
		},
		DragonRoar: {
			file: 'roar'
		},
		ShootFire: {
			file: 'dshoot'
		},
		ExplodeFire: {
			file: 'fireexplode'
		},
		Charge: {
			file: 'charge'
		},
		Ice: {
			file: 'ice'
		},
		Fire: {
			file: 'fire'
		},
		SegmentExplode: {
			file: 'dexplode'
		},
		DragonExplode: {
			file: 'dannihilate'
		},
		LichSpell: {
			file: 'lichspell'
		}
	};
	
	function loadSound(sound) {
		if(format != null) {
			toLoad++;
			provider.load(sound, CDN_PATH, format, loadCallback);
		}
	}
	
	function loadCallback(file, failed) {
		if(failed) {
			console.log("Loading sound " + file + " failed.");
		}
		toLoad--;
	}
	
	function chooseFormat() {
		var a = new Audio();
		if (!!(a.canPlayType && a.canPlayType('audio/ogg;').replace(/no/, ''))) {
			return "ogg";
		}
		if (!!(a.canPlayType && a.canPlayType('audio/mpeg;').replace(/no/, ''))) {
			return "mp3";
		}
		// Shouldn't need more formats
		return null;
	}
	
	function getProvider() {
		var p = WebAudioProvider.getInstance();
		if(p == null) {
			p = HtmlAudioProvider.getInstance();
		}
		return p;
	}
	
	function crossFade(outSound, inSound, time) {
		provider.enter && provider.enter(sounds[inSound]);
		provider.crossFade(sounds[outSound], sounds[inSound], time);
	}
	
	function startMusic() {
		if(!playingMusic) {
			playingMusic = true;
			GameAudio.play('DayMusic');
		}
	}
	
	function startBossMusic() {
		GameAudio.play('BossMusic');
		// If it's not night time, something is horribly wrong...
		crossFade('NightMusic', 'BossMusic', 500);
		playingBossMusic = true;
	}
	
	// музыка главного меню стартует с первого жеста (до него браузер не даёт играть) и гаснет, когда загружена игра
	function startMenu() {
		if(!playingMenu && !noMusic && document.body.className.indexOf('titleScreen') >= 0) {
			playingMenu = true;
			GameAudio.play('MenuMusic');
		}
	}
	
	function stopMenu() {
		if(playingMenu) {
			playingMenu = false;
			if(provider.fadeOut) {
				provider.fadeOut(sounds.MenuMusic, 1500);
			} else {
				GameAudio.stop('MenuMusic');
			}
		}
	}
	
	// новая игра+: день и ночь снова с первого трека (следующий вход в трек начнёт с первой части)
	function restartMusic() {
		if(playingMusic && provider.reset) {
			provider.reset(sounds.DayMusic);
			provider.reset(sounds.NightMusic);
		}
	}
	
	// титры: трек грузится заранее (при вызове дракона), а не при старте игры
	function prefetchEnding() {
		var s = sounds.EndingMusic;
		if(!noMusic && !s.requested && provider && format != null) {
			s.requested = true;
			loadSound(s);
		}
	}
	
	function startEnding() {
		if(playingEnding || noMusic || !provider || format == null) {
			return;
		}
		playingEnding = true;
		prefetchEnding();
		GameAudio.play('EndingMusic');
		var from = playingBossMusic ? 'BossMusic' : (require('app/engine').isNight() ? 'NightMusic' : 'DayMusic');
		endingFrom = from;
		crossFade(from, 'EndingMusic', 1500);
		setTimeout(function() {
			if(from == 'BossMusic') {
				GameAudio.stop('BossMusic');
			}
		}, 1800);
	}
	
	function stopEnding(inSound) {
		if(!playingEnding) {
			return false;
		}
		playingEnding = false;
		playingBossMusic = false;
		crossFade('EndingMusic', inSound, 1200);
		setTimeout(function() {
			GameAudio.stop('EndingMusic');
		}, 1500);
		return true;
	}
	
	function changeMusic(isNight) {
		if(stopEnding(isNight ? 'NightMusic' : 'DayMusic')) {
			return;
		}
		if(playingBossMusic) {
			crossFade('BossMusic', isNight ? 'NightMusic' : 'DayMusic', 500);
			GameAudio.stop('BossMusic');
			playingBossMusic = false;
		} else if(isNight) {
			crossFade('DayMusic', 'NightMusic', 700);
		} else {
			crossFade('NightMusic', 'DayMusic', 700);
		}
	}
	
	function getLootSound(loot) {
		switch(loot) {
		case 'healthPotion':
			return 'Heal';
		case 'bomb':
			return 'Bomb';
		case 'equipment':
			return 'Equip';
		}
	}
		
	function playLootSound(loot) {
		GameAudio.play(getLootSound(loot));
	}
	
	function toggleMute(mute) {
		GameAudio.setMusicVolume( mute ? 0 : require('app/gameoptions').get('musicVolume'), true);
		GameAudio.setEffectsVolume( mute ? 0 : require('app/gameoptions').get('effectsVolume'), true);
	}
	
	var GameAudio = {
		init: function(options) {
			options = options || {};
			if(!provider) { 
				try {
					provider = getProvider();
					format = chooseFormat();
					if(provider != null && format != null) {
						toLoad = 0;
						noMusic = !!options.nomusic;
						for(s in sounds) {
							if(!sounds[s].lazy && (!options.nomusic || !sounds[s].music)) {
								loadSound(sounds[s]);
							}
						}
						E.bind('dayBreak', startMusic);
						E.bind('gameLoaded', stopMenu);
						if(!options.nomusic) {
							['mousedown', 'touchstart', 'keydown'].forEach(function(ev) {
								document.addEventListener(ev, startMenu, true);
							});
						}
					}
				} catch(e) {
					console.error('Failed to init audio. Your browser sucks.');
					return;
				}
			} else {
				restartMusic();
				if(!stopEnding('DayMusic')) {
					crossFade(playingBossMusic ? 'BossMusic' : 'NightMusic', 'DayMusic', 700);
					if(playingBossMusic) {
						setTimeout(GameAudio.stop.bind(GameAudio, 'BossMusic'), 900);
					}
				}
			}
			playingBossMusic = false;
			
			E.bind('pause', function() { toggleMute(true); });
			E.bind('unpause', function() { toggleMute(false); });
			
			E.bind('tileDrop', GameAudio.play.bind(this, 'TileClick'));
			E.bind('setMusicVolume', GameAudio.setMusicVolume);
			E.bind('setEffectsVolume', GameAudio.setEffectsVolume);
			E.bind('phaseChange', changeMusic);
			E.bind('tilesCleared', GameAudio.play.bind(this, 'Match'));
			E.bind('bluntHit', GameAudio.play.bind(this, 'Blunt'));
			E.bind('sharpHit', GameAudio.play.bind(this, 'Slash'));
			E.bind('shieldHit', GameAudio.play.bind(this, 'ShieldHit'));
			E.bind('monsterHit', GameAudio.play.bind(this, 'MonsterHit'));
			E.bind('arrowHit', GameAudio.play.bind(this, 'ArrowHit'));
			E.bind('biteHit', GameAudio.play.bind(this, 'BiteHit'));
			E.bind('blockDown', GameAudio.play.bind(this, 'BlockDown'));
			E.bind('blockUp', GameAudio.play.bind(this, 'BlockUp'));
			E.bind('death', GameAudio.play.bind(this, 'Die'));
			E.bind('shoot', GameAudio.play.bind(this, 'Shoot'));
			E.bind('pickupLoot', GameAudio.play.bind(this, 'Open'));
			E.bind('prioritize', GameAudio.play.bind(this, 'BlockUp'));
			E.bind('deprioritize', GameAudio.play.bind(this, 'BlockDown'));
			E.bind('teleport', GameAudio.play.bind(this, 'Teleport'));
			E.bind('lootUsed', playLootSound);
			E.bind('tileExplode', GameAudio.play.bind(this, 'TileExplode'));
			E.bind('flap', GameAudio.play.bind(this, 'Wing'));
			E.bind('haste', GameAudio.play.bind(this, 'Haste'));
			E.bind('refreshBoardSpell', GameAudio.play.bind(this, 'RefreshBoard'));
			E.bind('phaseChangeSpell', GameAudio.play.bind(this, 'PhaseChange'));
			E.bind('freezeTime', GameAudio.play.bind(this, 'FreezeTime'));
			E.bind('levelUp', GameAudio.play.bind(this, 'LevelUp'));
			E.bind('landDragon', GameAudio.play.bind(this, 'DragonLand'));
			E.bind('roar', GameAudio.play.bind(this, 'DragonRoar'));
			E.bind('shootFire', GameAudio.play.bind(this, 'ShootFire'));
			E.bind('explodeFire', GameAudio.play.bind(this, 'ExplodeFire'));
			E.bind('charge', GameAudio.play.bind(this, 'Charge'));
			E.bind('ice', GameAudio.play.bind(this, 'Ice'));
			E.bind('burn', GameAudio.play.bind(this, 'Fire'));
			E.bind('segmentExplode', GameAudio.play.bind(this, 'SegmentExplode'));
			E.bind('dragonExplode', GameAudio.play.bind(this, 'DragonExplode'));
			E.bind('callDragon', startBossMusic.bind(this));
			E.bind('callDragon', prefetchEnding);
			E.bind('endingStart', startEnding);
			E.bind('lichSpell', GameAudio.play.bind(this, 'LichSpell'));
			
			GameAudio.setMusicVolume(require('app/gameoptions').get('musicVolume'));
			GameAudio.setEffectsVolume(require('app/gameoptions').get('effectsVolume'));
			
			longloadTimer = setTimeout(function() {
				E.trigger('longLoad');
			}, MUSIC_TIMEOUT);
		},
		
		isReady: function() {
			if(toLoad <= 0) { 
				clearTimeout(longloadTimer);
				return true;
			}
			return false;
		},
		
		setMusicVolume: function(volume, noSave) {
			!noSave && require('app/gameoptions').set('musicVolume', volume);
			provider.setMusicVolume(volume);
		},
		
		setEffectsVolume: function(volume, noSave) {
			!noSave && require('app/gameoptions').set('effectsVolume', volume);
			provider.setEffectsVolume(volume);
		},
		
		play: function(sound, silent) {
			var s = sounds[sound];
			if(s && provider) {
				provider.play(s, silent);
			}
		},
		
		stop: function(sound) {
			var s = sounds[sound];
			if(s && provider) {
				provider.stop(sounds[sound]);
			}
		}
	};
	
	return GameAudio;
});

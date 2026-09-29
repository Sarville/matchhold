define(function() {
	
	var context = null;
	var musicVolume = null;
	var effectsVolume = null;
	
	// Части играют в случайном порядке без повторов, пока не сыграны все; новый круг не начинается с только что сыгранной
	function shuffledParts(count, skip, last) {
		var bag = [];
		for(var i = 0; i < count; i++) {
			if(i !== skip) {
				bag.push(i);
			}
		}
		for(i = bag.length - 1; i > 0; i--) {
			var k = Math.floor(Math.random() * (i + 1)), t = bag[i];
			bag[i] = bag[k];
			bag[k] = t;
		}
		if(bag.length > 1 && bag[bag.length - 1] === last) {
			bag.unshift(bag.pop());
		}
		return bag;
	}

	function nextPart(sound) {
		if(!sound.bag.length) {
			sound.bag = shuffledParts(sound.parts, -1, sound.playingPart);
		}
		return sound.bag.pop();
	}

	function createSoundSource(sound, partNum) {
		var source = context.createBufferSource();
		if(sound.partsBuffer) {
			sound.playingPart = partNum;
			source.buffer = sound.partsBuffer[sound.playingPart];
			if(sound.music) {
				// Randomly switch to a different part each time one finishes
				source.onended = function() {
					WebAudioProvider.play(sound, nextPart(sound));
				};
			}
		} else {
			source.buffer = sound.buffer;
		}
		if(sound.music) {
			if(!sound.partsBuffer) {
				source.loop = true;
			}
			sound.volume = context.createGain();
			sound.volume.gain.value = 1;
			sound.volume.connect(musicVolume);
			source.connect(sound.volume);
		} else {
			source.connect(effectsVolume);
		}
		return source;
	}
	
	function isSoundReady(sound) {
		return (sound.parts && sound.partsBuffer && sound.partsBuffer[sound.playingPart || 0]) || sound.buffer;
	}
	
	function soundLoaded(sound, callback, partNum) {
		if(sound.playingPart != null && partNum != null && sound.playingPart == partNum) {
			WebAudioProvider.play(sound, partNum);
		} else if(sound.deferred) {
			sound.deferred = false;
			if(sound.playRequested) {
				WebAudioProvider.play(sound);
				sound.onLatePlay && sound.onLatePlay();
			}
		} else {
			callback(sound.file);
		}
	}
	
	function loadSound(sound, basePath, format, callback, partNum) {
		basePath = basePath || "";
		var request = new XMLHttpRequest();
		var isPart = partNum != null;
		if(isPart) {
			sound.partsBuffer = sound.partsBuffer || [];
		}
		request.open("GET", basePath + "audio/" + sound.file + (isPart ? "-" + partNum : "") + "." + format, true);
		request.responseType = "arraybuffer";
		request.onload = function() {
			if(sound.music && !sound.required) {
				sound.deferred = true;
				callback(sound.file);
			}
			context.decodeAudioData(request.response, function(buffer) {
				if(isPart) {
					sound.partsBuffer[partNum] = buffer;
					soundLoaded(sound, callback, partNum);
				} else {
					sound.buffer = buffer;
					soundLoaded(sound, callback);
				}
			});
		};
		request.send();
	}
	
	var WebAudioProvider = {
		getInstance: function() {
			if(typeof AudioContext !== 'undefined') {
				context = new AudioContext();
			} else if(typeof webkitAudioContext !== 'undefined') {
				context = new webkitAudioContext();
			} else {
				return null;
			}
			
			musicVolume = context.createGain();
			musicVolume.connect(context.destination);
			effectsVolume = context.createGain();
			effectsVolume.connect(context.destination);
			return WebAudioProvider;
		},
		
		load: function(sound, basePath, format, callback) {
			
			if(sound.parts != null) {
				for(var i = 0; i < sound.parts; i++) {
					(function(partNum) {
						setTimeout(function() {
//							console.log('loading part ' + partNum);
							loadSound(sound, basePath, format, callback, partNum);
						}, i * 3000);
					})(i);
				}
			} else {
				loadSound(sound, basePath, format, callback);
			}
		},
		
		play: function(sound, partNum) {
			if(partNum == null && sound.parts) {
				// свежий старт: всегда с первой части
				sound.bag = shuffledParts(sound.parts, 0, 0);
			}
			sound.playingPart = partNum || 0;
			if(isSoundReady(sound)) {
				var source = sound.currentSource = createSoundSource(sound, sound.playingPart);
				if(sound.silentIf && sound.silentIf() && sound.volume != null) {
					sound.volume.gain.value = 0;
				}
				source.start(0);
			} else {
//				console.log('play requested for ' + sound.file + ' part ' + partNum);
				sound.playRequested = true;
			}
		},
		
		stop: function(sound) {
			if(sound.currentSource) {
				sound.currentSource.stop(0);
			}
		},
		
		// заново с первой части, без автоперехода на случайную из onended
		restart: function(sound) {
			if(sound.currentSource) {
				sound.currentSource.onended = null;
				sound.currentSource.stop(0);
			}
			WebAudioProvider.play(sound);
		},
		
		fadeOut: function(sound, time) {
			var gain = sound.volume ? sound.volume.gain : null;
			(function fade() {
				if(gain && gain.value > 0) {
					gain.value = Math.max(gain.value - 0.1, 0);
					setTimeout(fade, time / 10);
				} else {
					WebAudioProvider.stop(sound);
				}
			})();
		},
		
		setMusicVolume: function(v) {
			if(musicVolume) {
				musicVolume.gain.value = v;
			}
		},
		
		setEffectsVolume: function(v) {
			if(effectsVolume) {
				effectsVolume.gain.value = v;
			}
		},
		
		crossFade: function(outSound, inSound, time) {
			// уходящий трек может быть не загружен: тогда просто вводим входящий
			if(isSoundReady(inSound) && inSound.volume) {
				var out = isSoundReady(outSound) && outSound.volume;
				(function fade() {
					if(out) {
						out.gain.value = Math.max(out.gain.value - 0.1, 0);
					}
					inSound.volume.gain.value = Math.min(inSound.volume.gain.value + 0.1, 1);
					if((out && out.gain.value > 0) || inSound.volume.gain.value < 1) {
						setTimeout(fade, time / 10);
					}
				})();
			}
		}
	};
	return WebAudioProvider;
});

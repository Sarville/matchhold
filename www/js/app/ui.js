define(['jquery', 'app/eventmanager', 'app/gameoptions'], function($, E, O) {

	var ICONS = {
		gear: 'M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.49.49 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.48.48 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z',
		music: 'M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z',
		sound: 'M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z',
		book: 'M21 5c-1.11-.35-2.33-.5-3.5-.5-1.95 0-4.05.4-5.5 1.5-1.45-1.1-3.55-1.5-5.5-1.5S2.45 4.9 1 6v14.65c0 .25.25.5.5.5.1 0 .15-.05.25-.05C3.1 20.45 5.05 20 6.5 20c1.95 0 4.05.4 5.5 1.5 1.35-.85 3.8-1.5 5.5-1.5 1.65 0 3.35.3 4.75 1.05.1.05.15.05.25.05.25 0 .5-.25.5-.5V6c-.6-.45-1.25-.75-2-1zm0 13.5c-1.1-.35-2.3-.5-3.5-.5-1.7 0-4.15.65-5.5 1.5V8c1.35-.85 3.8-1.5 5.5-1.5 1.2 0 2.4.15 3.5.5v11.5z',
		gamepad: 'M21 6H3c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2h18c1.1 0 1.99-.9 1.99-2L23 8c0-1.1-.9-2-2-2zm-10 7H8v3H6v-3H3v-2h3V8h2v3h3v2zm4.5 2c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm4-3c-.83 0-1.5-.67-1.5-1.5S18.67 9 19.5 9s1.5.67 1.5 1.5-.67 1.5-1.5 1.5z',
		export: 'M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z',
		import: 'M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z',
		delete: 'M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z',
		plus: 'M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z',
		leaf: 'M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C7 8 17 8 17 8z',
		sword: 'M20.49 3.51 19.78 8.46 12.00 16.24 7.76 12.00 15.54 4.22zM4.93 9.17 14.83 19.07 13.06 20.84 3.16 10.94zM7.19 14.97 9.03 16.81 5.85 19.99 4.01 18.15z',
		noads: 'M3 6h18a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1zm1 2v8h16V8H4zM2.6 20.2L20.2 2.6l1.2 1.2L3.8 21.4z'
	};

	var layers = [];
	var sentinel = false, leaving = false, pausedByUI = false, inited = false, settingsSeen = false;

	function G() { return require('app/graphics/graphics'); }
	function Eng() { return require('app/engine'); }
	function t(key) { return G().getText(key); }

	function icon(name) {
		return '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="' + ICONS[name] + '"/></svg>';
	}

	function click() {
		try { require('app/audio/audio').play('Click'); } catch(e) {}
	}

	function syncLayers() {
		var settings = layers.some(function(l) { return l.el.is('#settings'); });
		$('body').toggleClass('settingsOpen', settings).toggleClass('layerOpen', layers.length > 0);
		var want = layers.length > 0 && Eng().isStarted();
		if(want != pausedByUI) {
			pausedByUI = want;
			Eng().paused = want;
			if(!want) {
				E.trigger('afterUnpaused');
				if(settingsSeen) {
					settingsSeen = false;
					E.trigger('menuReturn');
				}
			}
		}
	}

	function push(el, locked) {
		el.addClass('open');
		if(el.is('#settings') && Eng().isStarted()) settingsSeen = true;
		layers.push({ el: el, locked: !!locked });
		syncLayers();
	}

	function pop() {
		var layer = layers.pop();
		if(layer) {
			layer.el.removeClass('open');
			syncLayers();
		}
	}

	// закрытие «извне» (фон, Escape, назад); locked-окно закрывают только его кнопки
	function dismiss() {
		var top = layers[layers.length - 1];
		if(top && !top.locked) pop();
	}

	function modal(o) {
		if(layers.length && layers[layers.length - 1].el.is('#modal')) {
			pop();
		}
		var el = $('#modal'), box = el.find('.panel').empty().attr('class', 'panel modalPanel ' + (o.cls || ''));
		box.append($('<h2>').text(t(o.title)));
		if(o.text) {
			box.append($('<p>').text(t(o.text)));
		}
		if(o.body) {
			box.append(o.body);
		}
		var row = $('<div class="btnRow">').appendTo(box);
		(o.buttons || []).forEach(function(b) {
			$('<button type="button">').addClass('btn ' + (b.cls || '')).text(t(b.text)).appendTo(row)
				.on('click', function() {
					if(!b.click || b.click.call(this) !== false) {
						pop();
					}
				});
		});
		push(el, o.locked);
	}

	function tokens(text) {
		var out = $('<span>');
		text.split(/\{(\w+)\}/).forEach(function(part, i) {
			if(i % 2 == 0) {
				out.append(document.createTextNode(part));
			} else if(part == 'star') {
				out.append('<i class="gi gs"></i>');
			} else {
				var i = $('<i class="gi">')[0];
				i.style.setProperty('--c', part.charAt(1));
				i.style.setProperty('--r', part.charAt(0) == 'n' ? 9 : 0);
				out.append(i);
			}
		});
		return out.contents();
	}

	function guide() {
		var body = $('<div class="guideBody">');
		t('GUIDE').forEach(function(sec) {
			var s = $('<section>').appendTo(body);
			s.append($('<h3>').text(sec.h));
			if(sec.img) {
				s.append($('<img class="guideImg" alt="">').attr('src', 'img/guide/' + sec.img + '.webp'));
			}
			sec.p.forEach(function(line) {
				s.append($('<p>').append(tokens(line)));
			});
		});
		modal({ title: 'HOW_TO_PLAY', cls: 'guidePanel', body: body, buttons: [{ text: 'CLOSE' }] });
	}

	function soon(title) {
		modal({ title: title, text: 'SOON_TEXT', buttons: [{ text: 'CLOSE' }] });
	}

	function leave() {
		if(sentinel) {
			leaving = true;
			history.back();
			setTimeout(function() { location.reload(); }, 400);
		} else {
			location.reload();
		}
	}

	function confirmExit() {
		modal({
			title: 'EXIT_TITLE', text: 'EXIT_TEXT',
			buttons: [{ text: 'EXIT', cls: 'danger', click: leave }, { text: 'CANCEL' }]
		});
	}

	function back() {
		if(layers.length) {
			dismiss();
			return true;
		}
		if(Eng().isStarted()) {
			confirmExit();
			return true;
		}
		return false;
	}

	function applyLang() {
		var lang = O.get('lang');
		document.documentElement.lang = lang;
		$('[data-i18n]').each(function() {
			$(this).text(t($(this).data('i18n')));
		});
		$('.logo .a').text(t('LOGO_A'));
		$('.logo .b').text(t('LOGO_B'));
		$('#btnLang').text(lang == 'ru' ? 'EN' : 'RU');
		$('.langSwitch button').each(function() {
			$(this).toggleClass('on', $(this).data('lang') == lang);
		});
	}

	function setLang(lang) {
		if(lang == O.get('lang')) return;
		O.set('lang', lang);
		G().setLocale(lang, function() {
			applyLang();
			G().drawSaveSlots();
		});
	}

	// ползунок: тянется мышью и пальцем, значение 0..1 уходит в игру сразу
	function bindBar(row) {
		var bar = row.find('.bar'), opt = row.data('opt'), event = opt == 'musicVolume' ? 'setMusicVolume' : 'setEffectsVolume';
		function move(e) {
			var r = bar[0].getBoundingClientRect(), pad = bar.find('.knob')[0].offsetWidth / 2;
			var v = Math.max(0, Math.min(1, (e.clientX - r.left - pad) / (r.width - 2 * pad)));
			bar[0].style.setProperty('--v', v);
			E.trigger(event, [v]);
			O.set(opt, v);
		}
		bar.on('pointerdown', function(e) {
			bar[0].setPointerCapture(e.originalEvent.pointerId);
			bar.data('drag', true);
			move(e.originalEvent);
		}).on('pointermove', function(e) {
			bar.data('drag') && move(e.originalEvent);
		}).on('pointerup pointercancel', function() {
			if(bar.data('drag')) {
				bar.data('drag', false);
				click();
			}
		});
	}

	// тумблер сложности: тап по половинке выбирает её, перетаскивание ползунка — по отпусканию ближе к какой стороне
	function bindDiff(diff) {
		var startX = 0, down = false;
		function pos(e) {
			e = e.originalEvent;
			var r = diff[0].getBoundingClientRect();
			return Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
		}
		diff.on('pointerdown', function(e) {
			diff[0].setPointerCapture(e.originalEvent.pointerId);
			down = true; startX = e.originalEvent.clientX;
		}).on('pointermove', function(e) {
			if(!down) return;
			if(Math.abs(e.originalEvent.clientX - startX) > 6) {
				diff.addClass('drag')[0].style.setProperty('--p', Math.max(0, Math.min(1, (pos(e) - 0.25) / 0.5)));
			}
		}).on('pointerup pointercancel', function(e) {
			if(!down) return;
			down = false;
			diff.removeClass('drag')[0].style.removeProperty('--p');
			setCasual(pos(e) < 0.5);
		});
	}

	function setCasual(casual) {
		if(casual != O.get('casualMode', false)) {
			O.set('casualMode', casual);
			E.trigger('difficultyChanged', [casual]);
			click();
		}
		syncSettings();
	}

	function syncSettings() {
		$('.volRow').each(function() {
			$(this).find('.bar')[0].style.setProperty('--v', O.get($(this).data('opt'), 1));
		});
		$('.diff').toggleClass('casual', O.get('casualMode', false));
	}

	function openSettings() {
		if(layers.length) return;
		syncSettings();
		push($('#settings'));
	}

	function init() {
		if(inited) return;
		inited = true;
		$('[data-icon]').each(function() {
			$(this).html(icon($(this).data('icon')));
		});
		$('.volRow').each(function() { bindBar($(this)); });
		bindDiff($('.diff'));
		syncSettings();

		$(document).on('click', '.btn, .langSwitch button', click);
		$('#btnSettings, .menuBtn').on('click', openSettings);
		$('#btnContinue, #btnBack').on('click', pop);
		$('#btnLang').on('click', function() { setLang(O.get('lang') == 'ru' ? 'en' : 'ru'); });
		$('.langSwitch button').on('click', function() { setLang($(this).data('lang')); });
		$('#btnHow').on('click', guide);
		$('#btnMore').on('click', function() { soon('MORE_GAMES'); });
		$('#btnExit').on('click', confirmExit);
		$('#btnAds').on('click', function() {
			require('app/platform').removeAds();
		});
		$('.overlay').on('click', function(e) {
			if(e.target == this) dismiss();
		});
		$(document).on('keydown', function(e) {
			if(e.key == 'Escape') back();
		});
		document.addEventListener('backbutton', function() {
			if(!back() && navigator.app && navigator.app.exitApp) {
				navigator.app.exitApp();
			}
		}, false);

		// запись в истории появляется только после первого касания: иначе Chrome пропускает её кнопкой «назад»
		document.addEventListener('click', function() {
			if(!sentinel) {
				history.pushState({ matchhold: 1 }, '');
				sentinel = true;
			}
		}, { once: true, capture: true });
		window.addEventListener('popstate', function() {
			if(leaving) {
				location.reload();
			} else if(sentinel) {
				sentinel = false;
				if(back()) {
					history.pushState({ matchhold: 1 }, '');
					sentinel = true;
				} else {
					history.back();
				}
			}
		});
	}

	return { init: init, icon: icon, modal: modal, applyLang: applyLang };
});

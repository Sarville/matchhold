define(['jquery', 'app/eventmanager'], function($, E) {

	// порядок по нарастанию силы монстра
	var MONSTERS = ['rat', 'zombie', 'skeleton', 'spider', 'imp', 'lizardman', 'hauntedArmour', 'warlock',
		'demon', 'earthElemental', 'waterElemental', 'fireElemental', 'lich'];
	// [класс ресурса, колонка в tiles.webp]
	var RESOURCES = [['grain', 0], ['wood', 2], ['stone', 1], ['clay', 3], ['cloth', 4], ['mana', 5]];
	var POTIONS = [['healthPotion', 'loot_health_potion'], ['manaPotion', 'loot_mana_potion']];
	var OTHER = ['DEATHS', 'NIGHTS', 'ROW', 'CASUALNIGHTS', 'SWAPPED', 'CHAIN', 'ATONCE', 'CAST', 'DRAGONS'];

	var DURATION = 105000;	// весь проплыв титров, мс
	var HOLD = 3000;		// пауза на последней надписи
	var SKIP_DELAY = 2000;
	var DEATH_ROW = 5, FRAME_MS = 150;

	var timers = [], raf = 0, observer = null, finished = false;

	function t(key) {
		return require('app/graphics/graphics').getText(key);
	}

	function fmt(n) {
		return (n || 0).toLocaleString(document.documentElement.lang || 'en');
	}

	function plural(forms, n) {
		var rule = 'other';
		try {
			rule = new Intl.PluralRules(document.documentElement.lang || 'en').select(n);
		} catch(e) {}
		return forms[rule] || forms.other;
	}

	function later(fn, ms) {
		timers.push(setTimeout(fn, ms));
	}

	function el(cls, text) {
		var e = $('<div>').addClass(cls);
		if(text != null) {
			e.text(text);
		}
		return e;
	}

	function tileIcon(col) {
		var i = $('<i class="gi">');
		i[0].style.setProperty('--c', col);
		i[0].style.setProperty('--r', 0);
		return i;
	}

	function itemIcon(file) {
		return $('<i class="crIco">').css('background-image', 'url(img/v2/' + file + '.webp)');
	}

	// ---------- титры ----------

	function monsterRow(cls, n) {
		return el('crItem crMon')
			.append(el('crMName', t('MON_' + cls)))
			.append($('<div>').addClass('crSprite ' + cls))
			.append(el('crMNum', fmt(n)));
	}

	// монстр стоит, падает (готовая анимация смерти), тает; на его месте число уезжает вправо, слева проступает имя
	function playMonster(row) {
		var sprite = row.find('.crSprite'), w = sprite.width(), h = sprite.height(), frame = 0;
		function pos(f, r) {
			sprite.css('background-position', -(f * w) + 'px ' + -(r * h) + 'px');
		}
		pos(0, 0);
		later(function step() {
			pos(frame, DEATH_ROW);
			if(++frame < 4) {
				later(step, FRAME_MS);
				return;
			}
			later(function() {
				row.addClass('melt');
				later(function() {
					row.addClass('num');
					later(function() {
						row.addClass('slide');
					}, 600);
				}, 700);
			}, 450);
		}, 500);
	}

	function resRow(icon, n) {
		return el('crItem crRes').append(icon).append($('<span>').text(fmt(n)));
	}

	function buildCredits(counts) {
		var c = $('<div id="credits" data-clickable>');
		var scroll = el('crScroll').appendTo(c);
		var kills = counts.KILLED || 0;

		scroll.append(el('crItem crTitle', t('CLEAR')));

		scroll.append(el('crItem crLead', t('END_KILLS_A')));
		scroll.append(el('crItem crBig', fmt(kills)));
		scroll.append(el('crItem crLead crAfter', plural(t('END_KILLS_B'), kills)));
		MONSTERS.forEach(function(cls) {
			if(counts['KILLED_' + cls] > 0) {
				scroll.append(monsterRow(cls, counts['KILLED_' + cls]));
			}
		});

		scroll.append(el('crItem crHead', t('END_RESOURCES')));
		scroll.append(el('crItem crLead', t('GATHERED')));
		scroll.append(el('crItem crBig', fmt(counts.GATHERED)));
		RESOURCES.forEach(function(r) {
			if(counts['GATHERED_' + r[0]] > 0) {
				scroll.append(resRow(tileIcon(r[1]), counts['GATHERED_' + r[0]]));
			}
		});

		scroll.append(el('crItem crHead', t('END_LOOT')));
		scroll.append(el('crItem crLead', t('LOOT')));
		scroll.append(el('crItem crBig', fmt(counts.LOOT)));
		scroll.append(el('crItem crLead', t('END_POTIONS')));
		POTIONS.forEach(function(p) {
			scroll.append(resRow(itemIcon(p[1]), counts['POTION_' + p[0]]));
		});

		scroll.append(el('crItem crHead', t('END_OTHER')));
		OTHER.forEach(function(key) {
			if(counts[key] != null) {
				scroll.append(el('crItem crRow').append($('<span>').text(t(key))).append($('<b>').text(fmt(counts[key]))));
			}
		});

		scroll.append(el('crItem crHead crThanks', t('END_THANKS')));
		return c;
	}

	function reveal(c, items) {
		if(!window.IntersectionObserver) {
			items.addClass('in');
			items.filter('.crMon').addClass('melt num slide');
			return;
		}
		observer = new IntersectionObserver(function(entries) {
			entries.forEach(function(e) {
				if(e.isIntersecting) {
					observer.unobserve(e.target);
					var item = $(e.target).addClass('in');
					if(item.hasClass('crMon')) {
						playMonster(item);
					}
				}
			});
		}, { root: c[0], rootMargin: '0px 0px -20% 0px' });
		items.each(function() {
			observer.observe(this);
		});
	}

	function scrollUp(c, scroll, done) {
		var vh = c.height(), y0 = vh, y1 = vh * 0.55 - scroll.outerHeight();
		var span = DURATION - HOLD, elapsed = 0, last = null;
		function frame(ts) {
			// после сворачивания вкладки не перескакиваем вперёд
			elapsed += last == null ? 0 : Math.min(ts - last, 100);
			last = ts;
			var p = Math.min(elapsed / span, 1);
			scroll[0].style.transform = 'translate3d(0,' + (y0 + (y1 - y0) * p) + 'px,0)';
			if(p < 1) {
				raf = requestAnimationFrame(frame);
			} else {
				later(done, HOLD);
			}
		}
		scroll[0].style.transform = 'translate3d(0,' + y0 + 'px,0)';
		raf = requestAnimationFrame(frame);
	}

	// ---------- итоговая статистика ----------

	function statRow(label, value, icon) {
		var row = el('stRow');
		if(icon) {
			row.append(icon);
		}
		return row.append($('<span>').text(label)).append($('<b>').text(fmt(value)));
	}

	function buildStats(counts) {
		var body = el('endBody');
		function section(head, rows) {
			body.append($('<h3>').text(t(head)));
			rows.forEach(function(r) {
				body.append(r);
			});
		}

		var monsters = [statRow(t('KILLED'), counts.KILLED).addClass('total')];
		MONSTERS.forEach(function(cls) {
			if(counts['KILLED_' + cls] > 0) {
				monsters.push(statRow(t('MON_' + cls), counts['KILLED_' + cls]));
			}
		});
		section('END_MONSTERS', monsters);

		var resources = [statRow(t('GATHERED'), counts.GATHERED).addClass('total')];
		RESOURCES.forEach(function(r) {
			if(counts['GATHERED_' + r[0]] > 0) {
				resources.push(statRow(t('RES_' + r[0]), counts['GATHERED_' + r[0]], tileIcon(r[1])));
			}
		});
		section('END_RESOURCES', resources);

		var loot = [statRow(t('LOOT'), counts.LOOT).addClass('total')];
		POTIONS.forEach(function(p) {
			loot.push(statRow(t('POTION_' + p[0]), counts['POTION_' + p[0]], itemIcon(p[1])));
		});
		section('END_LOOT', loot);

		var other = [];
		OTHER.forEach(function(key) {
			if(counts[key] != null) {
				other.push(statRow(t(key), counts[key]));
			}
		});
		section('END_OTHER', other);
		return body;
	}

	function showStats(counts, onContinue, onNewGame) {
		var box = $('<div id="endStats" class="overlay" data-clickable>');
		var panel = el('panel endPanel').appendTo(box);
		function button(key, handler) {
			return $('<button type="button" class="btn">').text(t(key)).on('click', function() {
				hide();
				handler();
			});
		}
		panel.append($('<h2>').text(t('END_STATS')));
		panel.append(buildStats(counts));
		panel.append(el('btnRow').append(button('CONTINUE', onContinue)).append(button('NEWGAMEPLUS', onNewGame)));
		$('body').append(box);
		box.css('left');
		box.addClass('open');
	}

	// ---------- вход/выход ----------

	function stop() {
		timers.forEach(clearTimeout);
		timers = [];
		cancelAnimationFrame(raf);
		if(observer) {
			observer.disconnect();
			observer = null;
		}
	}

	function hide() {
		stop();
		$('#credits').remove();
		$('#endStats').removeClass('open');
		setTimeout(function() {
			$('#endStats:not(.open)').remove();
		}, 300);
	}

	function play(counts, onContinue, onNewGame) {
		hide();
		$('#endStats').remove();
		finished = false;
		var c = buildCredits(counts);
		var skip = $('<button type="button" class="btn crSkip">').text(t('SKIP')).appendTo(c);

		function finish() {
			if(finished) {
				return;
			}
			finished = true;
			stop();
			showStats(counts, onContinue, onNewGame);
			setTimeout(function() {
				c.remove();
			}, 500);
		}

		skip.on('click', finish);
		$('body').append(c);
		c.css('left');
		c.addClass('open');
		reveal(c, c.find('.crItem'));
		scrollUp(c, c.find('.crScroll'), finish);
		later(function() {
			skip.addClass('show');
		}, SKIP_DELAY);
		E.trigger('endingStart');
	}

	return {
		play: play,
		hide: hide
	};
});

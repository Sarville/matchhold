define({
	DAY: 'Day',
	PLAY: 'Play',
	CLEAR: 'Clear!',
	CONTINUE: 'Continue',
	NEWGAMEPLUS: 'New Game +',
	LEVEL: 'Level',
	DEATHS: 'Deaths',
	NIGHTS: 'Nights Survived',
	ROW: 'Consecutive Nights Survived',
	SWAPPED: 'Tiles Swapped',
	CHAIN: 'Longest Chain',
	GATHERED: 'Resources Gathered',
	KILLED: 'Monsters Killed',
	ATONCE: 'Most Monsters at Once',
	LOOT: 'Loot Looted',
	CAST: 'Spells Cast',
	DRAGONS: 'Dragons Slain',
	CASUALNIGHTS: 'Casual Nights',
	DIFFICULTY: 'Difficulty',
	SHARE: 'Share',
	DONATE: 'Donate',
	NEWGAME: 'New Game',
	CONFIRM: 'Confirm',
	CANCEL: 'Cancel',
	IMPORT: 'Import',
	EXPORT: 'Export',
	DELETE: 'Delete',
	ARE_YOU_SURE: 'Are you sure?',
	EXPORT_CODE: 'Export code:',
	IMPORT_CODE: 'Import code:',
	LONG_LOAD: 'Man, this is taking a long time.',
	NO_MUSIC: 'Play without music?',
	LOGO_A: 'MATCHH',
	LOGO_B: 'LD',
	LOADING: 'Loading...',
	SETTINGS: 'Settings',
	BACK: 'Back',
	MUSIC: 'Music',
	SOUNDS: 'Sounds',
	EASY: 'Easy',
	NORMAL: 'Normal',
	HOW_TO_PLAY: 'How to play',
	REMOVE_ADS: 'Remove ads',
	MORE_GAMES: 'More games',
	EXIT_MENU: 'Exit to menu',
	EXIT_TITLE: 'Exit to menu?',
	EXIT_TEXT: 'The current day will start over.',
	EXIT: 'Exit',
	COPY: 'Copy',
	COPIED: 'Copied!',
	DELETE_TEXT: 'This save will be deleted for good.',
	SOON: 'Coming soon',
	SOON_TEXT: 'This part of the game is not ready yet.',
	PAUSED: 'Paused',
	TAP_TO_RESUME: 'Tap to resume',
	CLOSE: 'Close',
	GUIDE: [
		{ h: 'Match three', img: 'board', p: [
			'Swap neighbouring tiles. Three or more identical tiles in a row disappear and the hero gets the resource. Long chains and combos give more.'
		] },
		{ h: 'By day: resources', p: [
			'{d0} Grain heals the hero.',
			'{d2} Wood, {d1} stone, {d3} clay and {d4} cloth go to storage and construction.',
			'{d5} Mana builds up spell power.',
			'Storage is a grid of cubes next to the house, up to 30 units each. It grows with the hero level. When it is full, the oldest supplies are lost, so do not hoard.'
		] },
		{ h: 'Buildings', img: 'world', p: [
			'Storage and construction sites are to the right of the house. The bars show what is still missing. Tap the bars and a star {star} appears over the building: resources go there first. Tap again to remove it.',
			'• Blacksmith: swords, stronger hits at night.',
			'• Sawmill: shields, block damage at night.',
			'• Bricklayer and Weaver: night monsters from clay and cloth become stronger and give more XP.'
		] },
		{ h: 'What to upgrade first', p: [
			'1. Blacksmith and Sawmill: sword and shield help you survive the night.',
			'2. Bricklayer and Weaver: once you fight confidently, for the XP.',
			'Every building can be upgraded several times.'
		] },
		{ h: 'By night: what becomes what', img: 'night', p: [
			'At night tiles transform. Match them like this:',
			'{d2} → {n2} Shield',
			'{d1} → {n1} Sword',
			'{d0} → {n0} Zombie',
			'{d3} → {n3} Burrow: rat, spider and more',
			'{d4} → {n4} Skull: skeleton and more',
			'{d5} → {n5} Lich'
		] },
		{ h: 'Monsters and XP', p: [
			'Every matched monster tile summons a monster. More tiles and a higher Bricklayer or Weaver tier make it stronger. The shield takes hits, the sword boosts yours.',
			'Defeated monsters give XP. A new level fully heals you and adds health.'
		] },
		{ h: 'Goal', p: [
			'Survive the nights and grow stronger. What waits at the end of the road, you will find out yourself.'
		] },
		{ h: '3 tips', p: [
			'1. Before night, make sure your health is full: grain heals by day.',
			'2. Do not summon too many monsters at once: gather a shield and a sword first.',
			'3. Put the star on the building you need so resources are not wasted.'
		] }
	]
});

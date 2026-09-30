// Прод-бандл: almond + wrap => один js/app.js без глобальных require/define/requirejs/$/jQuery.
// Платформа выбирается переменной окружения MH_PLATFORM (её задаёт build_platform.py)
({
	appDir: "../www",
	baseUrl: "js/lib",
	dir: "../build",
	mainConfigFile: "../www/js/app.js",
	modules: [
		{
			name: "app/main",
			include: ["almond", "app/platform/" + process.env.MH_PLATFORM],
			insertRequire: ["app/main"]
		}
	],
	wrap: { start: "(function(){var $,jQuery,mhJq=function(x){$=jQuery=x};", end: "})();" },
	// jQuery кладёт себя в window.$/window.jQuery; передаём в переменные обёртки (у jQuery внутри свой локальный $, поэтому через функцию), чтобы модули без явной зависимости продолжили работать
	onBuildWrite: function(name, path, contents) {
		if(name == "jquery") {
			var out = contents.replace("(e.jQuery=e.$=x)", "mhJq(x)");
			if(out == contents) throw new Error("jquery: window assignment not found");
			return out;
		}
		return contents;
	},
	optimize: 'uglify',
	optimizeCss: 'standard',
	removeCombined: true
})

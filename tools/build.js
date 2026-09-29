({
	appDir: "../www",
	baseUrl: "js/lib",
	dir: "../build",
	mainConfigFile: "../www/js/app.js",
	modules: [ 
		{
			name: "app"
		}
	],
	optimize: 'uglify',
	optimizeCss: 'standard',
	removeCombined: true
})
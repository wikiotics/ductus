({
    // a custom build file for aloha in ductus.
    // Read the Ductus docs (http://docs.ductus.us) to find out how to use it.
    // adapted from aloha's default build-profile-with-common-plugins.js

    // see full list of build options at: https://github.com/jrburke/r.js/blob/master/build/example.build.js

    //The top level directory that contains your app. If this option is used
    //then it assumed your scripts are in a subdirectory under this path.
    //This option is not required. If it is not specified, then baseUrl
    //below is the anchor point for finding things. If this option is specified,
    //then all the files from the app directory will be copied to the dir:
    //output area, and baseUrl will assume to be a relative path under
    //this directory.
    appDir: "../../../../submodules/Aloha-Editor/src/",

    // paths to the fragments to insert before/after source files to turn them into a closure
    wrap: {
        startFile: "../../../../submodules/Aloha-Editor/build/aloha/closure-start.frag",
        endFile: "../../../../submodules/Aloha-Editor/build/aloha/closure-end.frag",
    },
    //By default, all modules are located relative to this path. If baseUrl
    //is not explicitly set, then all modules are loaded relative to
    //the directory that holds the build file. If appDir is set, then
    //baseUrl should be specified as relative to the appDir.
    baseUrl: "lib/",

    paths: {
		// These paths are the same setup as in aloha.js.
		// r.js doesn't process dynamic configuration and calls to
		// require() that don't list modules literally, so we need to
		// maintain this duplicate list

		// We don't include Aloha's patched jquery by default, the user
		// should do it himself.
		"jquery": "empty:",
    	//"jquery": 'vendor/jquery-1.7.2',

		// We do include Aloha's patched jquery-ui by default, but the
		// user can override it if he is adventurous.
		"jqueryui": 'vendor/jquery-ui-1.9m6',

		// For the repository browser
		'PubSub': 'vendor/pubsub/js/pubsub-unminified',
		'Class': 'vendor/class',
		'RepositoryBrowser': 'vendor/repository-browser/js/repository-browser-unminified',
		'jstree': 'vendor/jquery.jstree',              // Mutates jquery
		'jqgrid': 'vendor/jquery.jqgrid',              // Mutates jquery
		'jquery-layout': 'vendor/jquery.layout',     // Mutates jquery
		'jqgrid-locale-en': 'vendor/grid.locale.en', // Mutates jqgrid
		'jqgrid-locale-de': 'vendor/grid.locale.de', // Mutates jqgrid
		'repository-browser-i18n-de': 'vendor/repository-browser/js/repository-browser-unminified',
		'repository-browser-i18n-en': 'vendor/repository-browser/js/repository-browser-unminified',

		// Shortcuts for all common plugins
		"ui": "../plugins/common/ui/lib",
		"ui/vendor": "../plugins/common/ui/vendor",
		"ui/css": "../plugins/common/ui/css",
		"ui/nls": "../plugins/common/ui/nls",
		"ui/res": "../plugins/common/ui/res",
		"link": "../plugins/common/link/lib",
		"link/vendor": "../plugins/common/link/vendor",
		"link/css": "../plugins/common/link/css",
		"link/nls": "../plugins/common/link/nls",
		"link/res": "../plugins/common/link/res",
		"table": "../plugins/common/table/lib",
		"table/vendor": "../plugins/common/table/vendor",
		"table/css": "../plugins/common/table/css",
		"table/nls": "../plugins/common/table/nls",
		"table/res": "../plugins/common/table/res",
		"list": "../plugins/common/list/lib",
		"list/vendor": "../plugins/common/list/vendor",
		"list/css": "../plugins/common/list/css",
		"list/nls": "../plugins/common/list/nls",
		"list/res": "../plugins/common/list/res",
		"image": "../plugins/common/image/lib",
		"image/vendor": "../plugins/common/image/vendor",
		"image/css": "../plugins/common/image/css",
		"image/nls": "../plugins/common/image/nls",
		"image/res": "../plugins/common/image/res",
		"highlighteditables": "../plugins/common/highlighteditables/lib",
		"highlighteditables/vendor": "../plugins/common/highlighteditables/vendor",
		"highlighteditables/css": "../plugins/common/highlighteditables/css",
		"highlighteditables/nls": "../plugins/common/highlighteditables/nls",
		"highlighteditables/res": "../plugins/common/highlighteditables/res",
		"format": "../plugins/common/format/lib",
		"format/vendor": "../plugins/common/format/vendor",
		"format/css": "../plugins/common/format/css",
		"format/nls": "../plugins/common/format/nls",
		"format/res": "../plugins/common/format/res",
		"dom-to-xhtml": "../plugins/common/dom-to-xhtml/lib",
		"dom-to-xhtml/vendor": "../plugins/common/dom-to-xhtml/vendor",
		"dom-to-xhtml/css": "../plugins/common/dom-to-xhtml/css",
		"dom-to-xhtml/nls": "../plugins/common/dom-to-xhtml/nls",
		"dom-to-xhtml/res": "../plugins/common/dom-to-xhtml/res",
		"contenthandler": "../plugins/common/contenthandler/lib",
		"contenthandler/vendor": "../plugins/common/contenthandler/vendor",
		"contenthandler/css": "../plugins/common/contenthandler/css",
		"contenthandler/nls": "../plugins/common/contenthandler/nls",
		"contenthandler/res": "../plugins/common/contenthandler/res",
		"characterpicker": "../plugins/common/characterpicker/lib",
		"characterpicker/vendor": "../plugins/common/characterpicker/vendor",
		"characterpicker/css": "../plugins/common/characterpicker/css",
		"characterpicker/nls": "../plugins/common/characterpicker/nls",
		"characterpicker/res": "../plugins/common/characterpicker/res",
		"commands": "../plugins/common/commands/lib",
		"commands/vendor": "../plugins/common/commands/vendor",
		"commands/css": "../plugins/common/commands/css",
		"commands/nls": "../plugins/common/commands/nls",
		"commands/res": "../plugins/common/commands/res",
		"align": "../plugins/common/align/lib",
		"align/vendor": "../plugins/common/align/vendor",
		"align/css": "../plugins/common/align/css",
		"align/nls": "../plugins/common/align/nls",
		"align/res": "../plugins/common/align/res",
		"abbr": "../plugins/common/abbr/lib",
		"abbr/vendor": "../plugins/common/abbr/vendor",
		"abbr/css": "../plugins/common/abbr/css",
		"abbr/nls": "../plugins/common/abbr/nls",
		"abbr/res": "../plugins/common/abbr/res",
		"block": "../plugins/common/block/lib",
		"block/vendor": "../plugins/common/block/vendor",
		"block/css": "../plugins/common/block/css",
		"block/nls": "../plugins/common/block/nls",
		"block/res": "../plugins/common/block/res",
		"horizontalruler": "../plugins/common/horizontalruler/lib",
		"horizontalruler/vendor": "../plugins/common/horizontalruler/vendor",
		"horizontalruler/css": "../plugins/common/horizontalruler/css",
		"horizontalruler/nls": "../plugins/common/horizontalruler/nls",
		"horizontalruler/res": "../plugins/common/horizontalruler/res",
		"undo": "../plugins/common/undo/lib",
		"undo/vendor": "../plugins/common/undo/vendor",
		"undo/css": "../plugins/common/undo/css",
		"undo/nls": "../plugins/common/undo/nls",
		"undo/res": "../plugins/common/undo/res",
		"paste": "../plugins/common/paste/lib",
		"paste/vendor": "../plugins/common/paste/vendor",
		"paste/css": "../plugins/common/paste/css",
		"paste/nls": "../plugins/common/paste/nls",
		"paste/res": "../plugins/common/paste/res",

		// Shortcuts for some often used extra plugins (not all)
		"cite": "../plugins/extra/cite/lib",
		"cite/vendor": "../plugins/extra/cite/vendor",
		"cite/css": "../plugins/extra/cite/css",
		"cite/nls": "../plugins/extra/cite/nls",
		"cite/res": "../plugins/extra/cite/res",
		"flag-icons": "../plugins/extra/flag-icons/lib",
		"flag-icons/vendor": "../plugins/extra/flag-icons/vendor",
		"flag-icons/css": "../plugins/extra/flag-icons/css",
		"flag-icons/nls": "../plugins/extra/flag-icons/nls",
		"flag-icons/res": "../plugins/extra/flag-icons/res",
		"numerated-headers": "../plugins/extra/numerated-headers/lib",
		"numerated-headers/vendor": "../plugins/extra/numerated-headers/vendor",
		"numerated-headers/css": "../plugins/extra/numerated-headers/css",
		"numerated-headers/nls": "../plugins/extra/numerated-headers/nls",
		"numerated-headers/res": "../plugins/extra/numerated-headers/res",
		"formatlesspaste": "../plugins/extra/formatlesspaste/lib",
		"formatlesspaste/vendor": "../plugins/extra/formatlesspaste/vendor",
		"formatlesspaste/css": "../plugins/extra/formatlesspaste/css",
		"formatlesspaste/nls": "../plugins/extra/formatlesspaste/nls",
		"formatlesspaste/res": "../plugins/extra/formatlesspaste/res",
		"linkbrowser": "../plugins/extra/linkbrowser/lib",
		"linkbrowser/vendor": "../plugins/extra/linkbrowser/vendor",
		"linkbrowser/css": "../plugins/extra/linkbrowser/css",
		"linkbrowser/nls": "../plugins/extra/linkbrowser/nls",
		"linkbrowser/res": "../plugins/extra/linkbrowser/res",
		"imagebrowser": "../plugins/extra/imagebrowser/lib",
		"imagebrowser/vendor": "../plugins/extra/imagebrowser/vendor",
		"imagebrowser/css": "../plugins/extra/imagebrowser/css",
		"imagebrowser/nls": "../plugins/extra/imagebrowser/nls",
		"imagebrowser/res": "../plugins/extra/imagebrowser/res",
		"ribbon": "../plugins/extra/ribbon/lib",
		"ribbon/vendor": "../plugins/extra/ribbon/vendor",
		"ribbon/css": "../plugins/extra/ribbon/css",
		"ribbon/nls": "../plugins/extra/ribbon/nls",
		"ribbon/res": "../plugins/extra/ribbon/res",
		"toc": "../plugins/extra/toc/lib",
		"toc/vendor": "../plugins/extra/toc/vendor",
		"toc/css": "../plugins/extra/toc/css",
		"toc/nls": "../plugins/extra/toc/nls",
		"toc/res": "../plugins/extra/toc/res",
		"wai-lang": "../plugins/extra/wai-lang/lib",
		"wai-lang/vendor": "../plugins/extra/wai-lang/vendor",
		"wai-lang/css": "../plugins/extra/wai-lang/css",
		"wai-lang/nls": "../plugins/extra/wai-lang/nls",
		"wai-lang/res": "../plugins/extra/wai-lang/res",
		"headerids": "../plugins/extra/headerids/lib",
		"headerids/vendor": "../plugins/extra/headerids/vendor",
		"headerids/css": "../plugins/extra/headerids/css",
		"headerids/nls": "../plugins/extra/headerids/nls",
		"headerids/res": "../plugins/extra/headerids/res",
		"metaview": "../plugins/extra/metaview/lib",
		"metaview/vendor": "../plugins/extra/metaview/vendor",
		"metaview/css": "../plugins/extra/metaview/css",
		"metaview/nls": "../plugins/extra/metaview/nls",
		"metaview/res": "../plugins/extra/metaview/res",
		"listenforcer": "../plugins/extra/listenforcer/lib",
		"listenforcer/vendor": "../plugins/extra/listenforcer/vendor",
		"listenforcer/css": "../plugins/extra/listenforcer/css",
		"listenforcer/nls": "../plugins/extra/listenforcer/nls",
		"listenforcer/res": "../plugins/extra/listenforcer/res",
    },

    //Configure CommonJS packages. See http://requirejs.org/docs/api.html#packages
    //for more information.
    packagePaths: [],
    packages: [],

    //The directory path to save the output. If not specified, then
    //the path will default to be a directory called "build" as a sibling
    //to the build file. All relative paths are relative to the build file.
    dir: "./aloha",

    // rely on the build script to clear the output dir and copy our own plugins
    keepBuildDir: true,

    //How to optimize all the JS files in the build output directory.
    //Right now only the following values
    //are supported:
    //- "uglify": (default) uses UglifyJS to minify the code.
    //- "closure": uses Google's Closure Compiler in simple optimization
    //mode to minify the code. Only available if running the optimizer using
    //Java.
    //- "closure.keepLines": Same as closure option, but keeps line returns
    //in the minified files.
    //- "none": no minification will be done.
    optimize: "uglify",

    //See https://github.com/mishoo/UglifyJS for the possible values.
    uglify: {
        toplevel: true,
        ascii_only: true,
        beautify: false,
        max_line_length: 1000
    },

    closure: {
        CompilerOptions: {},
        CompilationLevel: 'SIMPLE_OPTIMIZATIONS',
        loggingLevel: 'WARNING'
    },

    //Allow CSS optimizations. Allowed values:
    //- "standard": @import inlining, comment removal and line returns.
    //Removing line returns may have problems in IE, depending on the type
    //of CSS.
    //- "standard.keepLines": like "standard" but keeps line returns.
    //- "none": skip CSS optimizations.
    //- "standard.keepComments": keeps the file comments, but removes line
    //returns.  (r.js 1.0.8+)
    //- "standard.keepComments.keepLines": keeps the file comments and line
    //returns. (r.js 1.0.8+)
    optimizeCss: "none",//"standard.keepLines",

    //If optimizeCss is in use, a list of of files to ignore for the @import
    //inlining. The value of this option should be a comma separated list
    //of CSS file names to ignore. The file names should match whatever
    //strings are used in the @import calls.
    cssImportIgnore: null,

    //Inlines the text for any text! dependencies, to avoid the separate
    //async XMLHttpRequest calls to load those dependencies.
    inlineText: true,

    useStrict: false,

    pragmas: {
		alohaLoadInEndClosure: true
    },

    //Skip processing for pragmas.
    skipPragmas: false,

    //If skipModuleInsertion is false, then files that do not use define()
    //to define modules will get a define() placeholder inserted for them.
    //Also, require.pause/resume calls will be inserted.
    //Set it to true to avoid this. This is useful if you are building code that
    //does not use require() in the built project or in the JS files, but you
    //still want to use the optimization tool from RequireJS to concatenate modules
    //together.
    skipModuleInsertion: false,

    //If it is not a one file optimization, scan through all .js files in the
    //output directory for any plugin resource dependencies, and if the plugin
    //supports optimizing them as separate files, optimize them. Can be a
    //slower optimization. Only use if there are some plugins that use things
    //like XMLHttpRequest that do not work across domains, but the built code
    //will be placed on another domain.
    optimizeAllPluginResources: false,

    findNestedDependencies: false,

    removeCombined: true,

    modules: [

        {
            name: "aloha",

			include: [
				// all common plugins
				"ui/ui-plugin",
				"link/link-plugin",
				"table/table-plugin",
				"format/format-plugin",
				"list/list-plugin",
				//"image/image-plugin",
				"highlighteditables/highlighteditables-plugin",
				//"dom-to-xhtml/dom-to-xhtml-plugin",
				"contenthandler/contenthandler-plugin",
				//"characterpicker/characterpicker-plugin",
				//"commands/commands-plugin",
				//"block/block-plugin",
				//"align/align-plugin",
				//"abbr/abbr-plugin",
				//"horizontalruler/horizontalruler-plugin",
				//"undo/undo-plugin",
				//"paste/paste-plugin",
			],
        },

    ],

    // use a multiline string to build the regexp so git diffs stay readable
    fileExclusionRegExp: '(^demo$|' +
                         '^test$|' +
                         '^bg.png$|' +
                         '^package.json$|' +
                         '^abbr$|' +
                         '^align$|' +
                         '^attributes$|' +
                         '^browser$|' +
                         '^captioned-image$|' +
                         '^characterpicker$|' +
                         '^cite$|' +
                         '^commands$|' +
                         '^comments$|' +
                         '^dom-to-xhtml$|' +
                         '^draganddropfiles$|' +
                         '^flag-icons$|' +
                         '^formatlesspaste$|' +
                         '^googletranslate$|' +
                         '^headerids$|' +
                         '^horizontalruler$|' +
                         '^hints$|' +
                         '^image$|' +
                         '^imagebrowser$|' +
                         '^linkbrowser$|' +
                         '^linkchecker$|' +
                         '^linklist.js$|' +
                         '^listenforcer$|' +
                         '^metaview$|' +
                         '^numerated-headers$|' +
                         '^profiler$|' +
                         '^proxy$|' +
                         '^ribbon$|' +
                         '^sourceview$|' +
                         '^speak$|' +
                         '^toc$|' +
                         '^undo$|' +
                         '^wai-lang$|' +
                         '^zemanta$|' +
                         '^jquery-1.5.*$|' +
                         '^jquery-1.6.*$|' +
                         '^jquery-1.7.1.js$|' +
                         '^aloha-sidebar.css$|' +
                         '^repository-browser$|' +
                         '^\\.)',

    preserveLicenseComments: true,

    //Sets the logging level. It is a number. If you want "silent" running,
    //set logLevel to 4. From the logger.js file:
    //TRACE: 0,
    //INFO: 1,
    //WARN: 2,
    //ERROR: 3,
    //SILENT: 4
    //Default is 0.
    logLevel: 0,

})

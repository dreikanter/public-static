# public-static

A small Python script used to build single-page¹ static website from [Markdown](http://daringfireball.net/projects/markdown) source, [Mustache](http://mustache.github.com) template and [Skeleton](http://getskeleton.com) CSS framework. Created ~~to maintain author's homepage~~ for fun. Inspired by [addmeto.cc](https://github.com/bobuk/addmeto.cc) and couple of other geeky projects.

¹ — two pages will be Ok too.

## Installation

The script could be installed by command:

	pip install -e git+git://github.com/dreikanter/wp2md#egg=wp2md

It will install `ps` script itself and the following dependencies:

* `baker` — command line library.
* `pystache` — Mustache template parser implementation for Python.
* `python-markdown` — [Markdown](http://daringfireball.net/projects/markdown/) parser for Python.
* `yuicompressor` — CSS/Javascript Minificator.

Example website sources could be downloaded directly from GitHub:

	git clone git://github.com/dreikanter/public-static.git

Please keep in mind that the example website configuration uses Yahoo's yuicompressor for CSS/JS minification. To use this tool Java runtime should be properly installed in addition to Python's package. Eitherway there will be meaningless error message during attempt to run yuicompressor.

## Usage

Command line format:

	python ps.py <command> [parameters]

Available commands:

* `build` — generate web content.
* `preview` — run local web server to preview generated web site.

	* `-b` or `--browse` — opens site preview in default browser (disabled by default).
	* `-p` or `--port=HTTP-PORT` — save script output to log file (default value is 8000).

* `publish` — synchronize remote web server with generated content.
* `clean` — delete all generated web content.

Common parameters:

* `-c` or `--config=CONFIG` — specify configuration file. Default is `ps.ini`.
* `-s` or `--section=SECTION` — specify configuration file section. Default is the first one.
* `-l` or `--logfile=LOGFILE` — save script output to log file.
* `-h` or `--help` — show command line help.

## Configuration file

To avoid over-complicated command line syntax, main site building parameters intended to be kept in configuration file with an ordinary [RFC-822](http://www.ietf.org/rfc/rfc0822) compliant syntax.

By default `ps` command uses default configuration file `build.conf` located in the current working directory (not necessarily the directory where script itself resides!). Nevertheless the configuration file name and location could be changed arbitrary from the command line.

A single configuration file could contain more than one section. This allows to keep building configuration for multiple web sites or different building profiles for a single one — e.g. production and debug versions.

As it was mentioned script takes the first section from configuration file if the section name is not defined explicitly by the command line parameter. 

Build configuration parameters:

* `pages_path` — path to the page files directory.
* `static_path` — path to static resources (graphics, JS, CSS, etc) which should be copied to the generated website as is. JS and CSS files could be optionally minified (see details below).
* `templates_path` — [mustache](http://mustache.github.com) templates directory path.
* `build_path` — destination path where static website should be built.
* `minify_css` — yes/no to enable or disable CSS minification.
* `minify_js` — same thing for JavaScript.
* `run_browser_cmd` — OS-specific command to open an URL with a web browser. Used during generated website preview.
* `browser_opening_delay` — number of seconds between preview webserver start and browser execution. Default value is 2.0 and it's
 
Example:

	[example.com]
	author = Vasiliy Pupkin
	pages_path = ./pages
	static_path = ./static
	build_path = ./www
	templates_path = ./templates
	template = default
	run_browser_cmd = start {url}
	port = 8000
	browser_opening_delay = 2
	generator = {name} {version}
	minify_js = yes
	minify_css = yes
	minify_less = yes
	minify_js_cmd = yuicompressor --type js --nomunge -o {dest} {source}
	minify_css_cmd = yuicompressor --type css -o {dest} {source}
	publish_cmd = c:\bin\winscp\winscp.com /log=publish.log /command "open ""username@example.com""" "synchronize remote {path} ./example.com/public_html" "close" "exit"
	less_cmd = lessc {source} > {dest}

## Page file format

Each page is a plain text/markdown file complemented with a basic the metadata header. The format is pretty straightforward. Here is an example:

	title: Hello World!
	ctime: 2012-06-05 13:49:38
	mtime: 2012-06-05 13:49:38
	template: default
	custom-field: Custom field value

	# Hello world!

	This is the main page contents section.

Few important details:

* All header fields are optional and could omitted. But it's good to have at least a title for each page.
* `ctime`/`mtime` should comply the default format which is `YYYY-MM-DD HH:MM:SS`.
* Template value will be transformed to `[templates_path]\[template_name].mustache` file name where `templates_path` is defined by configuration and `template_name` is the `template` field value.
* All header fields are available from templates by names. E.g. `{{title}}` (see [mustache documentation](http://mustache.github.com/mustache.5.html) for template format details).
* Any number of custom header fields could be added.
* Custom field names should consist of alphanumeric characters, dashes and underscores. All names are case-sensitive.
* Page header fields could have single-line values only.
* Everything beneath the header is treated as page content. Template name for this section is `{{{content}}}` (triple curly bracing is used to prevent Mustache from HTML special characters escaping).

## Migrating from Wordpress

There is a great tool to export Wordpress data to PS-compatible files: [wp2md](https://github.com/dreikanter/wp2md).

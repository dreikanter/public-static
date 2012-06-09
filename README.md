# public-static

A small Python script used to build single-page¹ static website from [Markdown](http://daringfireball.net/projects/markdown) source, [Mustache](http://mustache.github.com) template and [Skeleton](http://getskeleton.com) CSS framework. Created <s>to maintain author's homepage</s> for fun. Inspired by [addmeto.cc](https://github.com/bobuk/addmeto.cc) and couple of other geeky projects.

¹ — two pages will be Ok too.

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
* `-s` or `--section=SECTION` — specify configuration file section. Default is `[ps]`.
* `-l` or `--logfile=LOGFILE` — save script output to log file.
* `-h` or `--help` — show command line help.

Configuration file:

To avoid over-complicated command line syntax, main site building parameters intended to be kept in configuration file with an ordinary [RFC-822](http://tools.ietf.org/html/rfc822.html) compliant syntax. As it was mentioned already default section name is `builder` but a single configuration file could contain multiple sections for different web sites to be maintained.

[TBD]


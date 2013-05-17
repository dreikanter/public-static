# public-static

A python script to build static websites from [Markdown](http://daringfireball.net/projects/markdown) source and [Jinja2](http://jinja.pocoo.org). Inspired by [Jekyll](http://jekyllrb.com) and [addmeto.cc](https://github.com/bobuk/addmeto.cc).

## Installation

The script could be installed directly from GitHub:

	pip install -e git+git://github.com/dreikanter/public-static#egg=public-static

Please keep in mind that the example website configuration uses Yahoo's yuicompressor for CSS and JavaScript minification. To use this tool [Java runtime](http://www.java.com/en/download/index.jsp) should be preinstalled.

## Basic usage

The following command creates a new website source in the current directory:

	pub init

Next you free to add any amount of posts or pages:

	pub post "Hello World!"
	pub page "About"

The site could be previewed right on the local host:

	pub run -b

The second argument here (`-b`) tells public-static to open the system default browser. Use `--help` for detailed command line arguments description.

## Page file format

Each page is a plain text/markdown file complemented with the  optional metadata in the header. The format is pretty straightforward. Here is an example:

	title: Hello World!
	created: 2012-06-05 13:49:38
	updated: 2012-06-05 13:49:38
	template: default
	custom-field: Custom field value

	# Hello world!

	This is the main page contents section.

Some details:

* All header fields are optional. The whole header could be omitted if you lazy enough.
* Both `created` and `updated` field values should comply the default format which is `YYYY-MM-DD HH:MM:SS`.
* `template` value is to be transformed to `[tpl_path]\[name].html` file name where `tpl_path` is defined by configuration and `name` is what specified in the page header.
* All header fields are accessible from template body by name. E.g. `{{title}}` will be replaced by the actual title if it's specified.
* Any number of custom header fields could be added.
* Custom field names should consist of alphanumeric characters, dashes and underscores. All names are case-sensitive.
* Page header fields could have single-line values only.
* Everything beneath the key-value header definition is to be treated as page content. Template name for this section is `{{ content }}`.

## Content migration

There is a great tool to export Wordpress data to public-static-compatible files: [wp2md](https://github.com/dreikanter/wp2md).

Copyright &copy; 2012 by [Alex Musayev](http://alex.musayev.com).
License: MIT (see [LICENSE](https://raw.github.com/dreikanter/public-static/master/LICENSE)).
Project home: [https://github.com/dreikanter/public-static](https://github.com/dreikanter/public-static).

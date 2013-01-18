# public-static

A small Python script used to build static websites from [Markdown](http://daringfireball.net/projects/markdown) source, [Jinja2](http://jinja.pocoo.org) templates and [Twitter Bootstrap](http://getskeleton.com) framework. Inspired by [Jekyll](http://jekyllrb.com), [Octopress](http://octopress.org), [addmeto.cc](https://github.com/bobuk/addmeto.cc), and couple of other geeky projects.

## Installation

The script could be installed directly from GitHub (dependent packages will be pulled automatically):

	pip install -e git+git://github.com/dreikanter/public-static#egg=public-static

Also you can clone project sources and test scripts from repository:

	git clone git://github.com/dreikanter/public-static.git

Please keep in mind that the example website configuration uses Yahoo's yuicompressor for CSS and JavaScript minification. To use this tool [Java runtime](http://www.java.com/en/download/index.jsp) should be properly installed in addition to Python package. Either way there will be meaningless error message during attempt to run yuicompressor.

## Basic usage

The following command will create new website instance in the current directory:

	pub init

Than you can create new posts or pages:

	pub post "Hello World!"
	pub page "About"

After some content created the site could be previewed right on the local host (`-b` option tells public-static to open the system default browser):

	pub run -b

Use `--help` for detailed command line arguments description.

## Page file format

Each page is a plain text/markdown file complemented with a basic the metadata header. The format is pretty straightforward. Here is an example:

	title: Hello World!
	created: 2012-06-05 13:49:38
	updated: 2012-06-05 13:49:38
	template: default
	custom-field: Custom field value

	# Hello world!

	This is the main page contents section.

Few important details:

* All header fields are optional and could omitted. But it's good to have at least a title for each page.
* `created`/`updated` should comply the default format which is `YYYY-MM-DD HH:MM:SS`.
* Template value will be transformed to `[tpl_path]\[name].html` file name where `tpl_path` is defined by configuration and `name` is the `template` field value.
* All header fields are available from templates by names. E.g. `{{title}}` (see [jinja documentation](http://jinja.pocoo.org/docs) for template format details).
* Any number of custom header fields could be added.
* Custom field names should consist of alphanumeric characters, dashes and underscores. All names are case-sensitive.
* Page header fields could have single-line values only.
* Everything beneath the header is treated as page content. Template name for this section is `{{ content }}`.

There is a great tool to export Wordpress data to public-static-compatible files: [wp2md](https://github.com/dreikanter/wp2md).

Copyright &copy; 2012 by [Alex Musayev](http://alex.musayev.com).  
License: MIT (see [LICENSE](https://raw.github.com/dreikanter/public-static/master/LICENSE)).  
Project home: [https://github.com/dreikanter/public-static](https://github.com/dreikanter/public-static).  

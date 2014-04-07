# public-static

This is a static website builder with the following features:

- Works out of the box.
- Capable for blogs and websites with arbitrary content structure.
- Uses [markdown](http://en.wikipedia.org/wiki/Markdown) page sources and [Jinja2](http://jinja.pocoo.org) templates.
- Includes neat and responsive default theme based on [Twitter Bootstrap 3](http://getbootstrap.com).
- Provides optional JavaScript, CSS and HTML minification.
- Can generate [sitemap.xml](http://sitemaps.org), [robots.txt](http://robotstxt.org), [humans.txt](http://humanstxt.org), and atom feed for blog posts.
- Supports [LESS](http://lesscss.org) stylesheets.
- Local host site preview.
- Code hightlighting based on [Google Code Prettify](https://code.google.com/p/google-code-prettify).
- Supports Disqus comments and Google Analytics.
- Tags.

## Installation

The latest stable version could be installed from PyPI:

	pip install publicstatic

Use this command to install latest development version directly from GitHub:

	pip install -e git+git://github.com/dreikanter/public-static#egg=public-static

Default website configuration uses Yahoo's yuicompressor for CSS and JavaScript minification. To use this tool [Java runtime](http://www.java.com/en/download/index.jsp) should be preinstalled.

## Basic usage

The following command creates a new website source in the current directory:

	pub init

Use the following commands to add posts or pages:

	pub post "Good news everyone!"
	pub page "True story"

With default configuration this commands will create a new post supposed to be located at `http://example.com/posts/good-news-everyone`, and a page `http://example.com/true-story`.

After adding some content the website should be built.

	pub build

This command will generate HTML pages using text content and template files. Build output will also include CSS files and any other assets included to the website source. Generated website could be previewed right on the local host:

	pub run -b

`-b` option tells public-static to open site root page using the default browser.

The last operation is to deploy generated web content to the destination server:

	pub deploy

This command suppose to use external tool like `rsync` or `aws` to synchronize local web content directory to the remote one. The actual command should be predefined in the configuration file as `deploy_cmd` parameter value. See some [examples on wiki](https://github.com/dreikanter/public-static/wiki/Content-deployment).

Use `--help` for detailed command line arguments description.

## Page file format

Each page is a plain text/markdown file complemented with the  optional metadata in the header. The format is pretty straightforward. Here is an example:

	title: Hello World!
	updated: 2012-06-05 13:49:38
	template: default
	custom-field: Custom field value

	# Hello world!

	This is the main page contents section.

Some details:

- All header fields are optional. The whole header could be omitted if you lazy enough.
- Both `created` and `updated` field values should comply the default format which is `YYYY-MM-DD HH:MM:SS`.
- `template` value is to be transformed to `[tpl_path]\[name].html` file name where `tpl_path` is defined by configuration and `name` is what specified in the page header.
- All header fields are accessible from template body by name. E.g. `{{title}}` will be replaced by the actual title if it's specified.
- Any number of custom header fields could be added.
- Custom field names should consist of alphanumeric characters, dashes and underscores. All names are case-sensitive.
- Page header fields could have single-line values only.
- Everything beneath the key-value header definition is to be treated as page content. Template name for this section is `{{ content }}`.

## Configuration

Public-static configuration resides in a yaml-formatted file `pub.conf` in the root of each website directory. `init` comand generates this file with default parameter values and a brief comment for each of them. Configuration supposed to be updated after site creation to fit user requirements like site structure, deployment destination, etc.

## Content migration

There is a great tool to export Wordpress data to public-static-compatible files: [wp2md](https://github.com/dreikanter/wp2md).

## Troubleshooting

- `pub` command is not available after installation.  

  If [pyenv](https://github.com/yyuu/pyenv) is used for Python version management, run `pyenv rehash` after calling pip install.

## Licensing

Copyright &copy; 2013 by [Alex Musayev](http://alex.musayev.com). License: [MIT](https://github.com/dreikanter/public-static/blob/master/LICENSE.md).

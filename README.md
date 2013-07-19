# public-static

A python script to build static websites from [Markdown](http://daringfireball.net/projects/markdown) source and [Jinja2](http://jinja.pocoo.org) templates. Inspired by [Jekyll](http://jekyllrb.com) and [addmeto.cc](https://github.com/bobuk/addmeto.cc).

## Installation

The script could be installed directly from GitHub:

```bash
pip install -e git+git://github.com/dreikanter/public-static#egg=public-static
```

Default website configuration uses Yahoo's yuicompressor for CSS and JavaScript minification. To use this tool [Java runtime](http://www.java.com/en/download/index.jsp) should be preinstalled.

## Basic usage

The following command creates a new website source in the current directory:

```bash
pub init
```

Use the following commands to add posts or pages:

```bash
pub post "Good news everyone!"
pub page "True story"
```

With default configuration this commands will create a new post supposed to be located at `http://example.com/posts/good-news-everyone`, and a page `http://example.com/true-story`.

After adding some content the website should be built.

```bash
pub build
```

This command will generate HTML pages using text content and template files. Build output will also include CSS files and any other assets included to the website source. Generated website could be previewed right on the local host:

```bash
pub run -b
```

`-b` option tells public-static to open site root page using the default browser.

The last operation is to deploy generated web content to the destination server:

```bash
pub deploy
```

It suppose to use external tool like `rsync`, `lftp`, or `s3cmd` to synchronize local web content directory with the remote one. The actual command should be predefined in the configuration file.

The following configuration example uses [s3 tool](http://s3.codeplex.com) to deploy to an Amazon S3 bucket:

```yaml
deploy_cmd: s3 put drafts.cc {build_path}\* /sub:withdelete /yes /sync /acl:public-read /nogui
```

`deploy_cmd` here is a configuration parameter definind an actual command behing `pub deploy`. And `{build_path}` will be replaced by public-static to the actual build path.

Use `--help` for detailed command line arguments description.

## Page file format

Each page is a plain text/markdown file complemented with the  optional metadata in the header. The format is pretty straightforward. Here is an example:

```markdown
title: Hello World!
created: 2012-06-05 13:49:38
updated: 2012-06-05 13:49:38
template: default
custom-field: Custom field value

# Hello world!

This is the main page contents section.
```

Some details:

* All header fields are optional. The whole header could be omitted if you lazy enough.
* Both `created` and `updated` field values should comply the default format which is `YYYY-MM-DD HH:MM:SS`.
* `template` value is to be transformed to `[tpl_path]\[name].html` file name where `tpl_path` is defined by configuration and `name` is what specified in the page header.
* All header fields are accessible from template body by name. E.g. `{{title}}` will be replaced by the actual title if it's specified.
* Any number of custom header fields could be added.
* Custom field names should consist of alphanumeric characters, dashes and underscores. All names are case-sensitive.
* Page header fields could have single-line values only.
* Everything beneath the key-value header definition is to be treated as page content. Template name for this section is `{{ content }}`.

## Configuration

Public-static configuration resides in a yaml-formatted file `pub.conf` in the root of each website directory. `init` comand generates this file with default parameter values and a brief comment for each of them. Configuration supposed to be updated after site creation to fit user requirements like site structure, deployment destination, etc.

## Content migration

There is a great tool to export Wordpress data to public-static-compatible files: [wp2md](https://github.com/dreikanter/wp2md).

Copyright &copy; 2012 by [Alex Musayev](http://alex.musayev.com).  
License: MIT (see [LICENSE](https://raw.github.com/dreikanter/public-static/master/LICENSE)).  
Project home: [https://github.com/dreikanter/public-static](https://github.com/dreikanter/public-static).

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

This command suppose to use external tool like `rsync` or `aws` to synchronize local web content directory to the remote one. The actual command should be predefined in the configuration file as `deploy_cmd` parameter value. Here are some examples. In each case `{build_path}` will be replaced to the actual local build path.

- Uploading content with `rsync` via SSH:
```
rsync -avz {build_path} <username>@<host>:/website/public_html/
```
  Username host and path to the destination directory should be replaced with actual values. Password-less SSH login will also be very helpful here.

- Using [aws-cli](https://github.com/aws/aws-cli) to upload files to S3 bucket (this is a recomended crossplatform solution):
```
aws s3 sync {build_path} s3://example.com --acl public-read --delete
```
  This assumes the aws [authentication setup](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-set-up.html) is already performed. `example.com` should be replaced with the actual bucket name.

- Using [s3 tool](http://s3.codeplex.com) on Windows:
```
s3 put example.com {build_path}\* /sub:withdelete /yes /sync /acl:public-read /nogui
```
  This also requires authentication setup.

- Synchronizing through FTP with `lftp`:
```
lftp -c "open -u <user>,<password> <host>; mirror -c -e -R -L {build_path} <path to>"
```

Use `--help` for detailed command line arguments description.

## Page file format

Each page is a plain text/markdown file complemented with the  optional metadata in the header. The format is pretty straightforward. Here is an example:

```markdown
title: Hello World!
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

Copyright &copy; 2013 by [Alex Musayev](http://alex.musayev.com).  
License: [MIT](https://github.com/dreikanter/public-static/blob/master/LICENSE.md).  
Project home: [https://github.com/dreikanter/public-static](https://github.com/dreikanter/public-static).

# coding: utf-8

# Site configuration file name
CONF_NAME = 'conf.yml'

# Configuration file header
CONF_HEADER = 'public-static configuration file'

# environment variable name to override 'verbose' configuration parameter
ENV_VERBOSE = 'ps_verbose'

# Program name and version info
GENERATOR = 'public-static'

# Program home page
GENERATOR_URL = 'http://github.com/dreikanter/public-static'

# Logger message timestamp format
LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

# Logger message format
LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"

# program name for CLI
PROG = 'pub'

# page prototype
PROTO_PAGE = """title: {title}
created: {created}

# {title}

This is a new page."""

# blog post prototype
PROTO_POST = """title: {title}
created: {created}
tags: unsorted

This is a new blog post."""

# sitemap file name
SITEMAP = 'sitemap.xml'

# relative path to theme assets inside site source directory
ASSETS_DIR = 'assets'

# relative path to custom templates inside site source directory
TEMPLATES_DIR = 'templates'

# relative path to theme assets inside site source directory
THEME_DIR = 'theme'

# relative path to theme assets inside site source directory
THEME_ASSETS_DIR = 'theme/' + ASSETS_DIR

# relative path to theme templates inside package and site source directory
THEME_TEMPLATES_DIR = 'theme/' + TEMPLATES_DIR

# prototype for the site source directory, located within the package directory
PROTO_DIR = 'prototype'

# page files directory path inside website source dir
PAGES_DIR = 'pages'

# post files directory path inside website source dir
POSTS_DIR = 'posts'

# directory name for data files
DATA_DIR = 'data'

# default build output directory path inside website source dir
BUILD_DIR = 'build'

# default post name
UNTITLED_POST = 'untitled-post'

# post file prefix format
PREFIX_FORMAT = '%Y%m%d'

# parameters sequence for the configuration file
EXPORTS = [
    'author',
    'author_url',
    'author_twitter',
    'build_path',
    'default_tags',
    'deploy_cmd',
    'disqus_id',
    'editor_cmd',
    'enable_search_form',
    'addthis_id',
    'google_analytics_id',
    'less_cmd',
    'menu',
    'min_css',
    'min_css_cmd',
    'min_html',
    'min_js',
    'min_js_cmd',
    'pluso_enabled',
    'port',
    'post_location',
    'root_url',
    'site_twitter',
    'source_url',
    'subtitle',
    'title',
    'verbose',
]

# configuration parameters
DEFAULTS = {
    'archive_location': {
        'value': 'archive.html',
        'desc': 'Blog archive page location',
    },
    'atom_location': {
        'value': 'atom.xml',
        'desc': 'Atom feed file name',
    },
    'author': {
        'value': 'Anonymous',
        'desc': 'Primary author name',
    },
    'author_twitter': {
        'value': '',
        'desc': 'Primary author twitter account',
    },
    'author_url': {
        'value': 'http://example.net',
        'desc': 'Primary author home page',
    },
    'build_path': {
        'value': BUILD_DIR,
        'desc': 'Build path for web content generator output',
    },
    'default_tags': {
        'value': ['misc'],
        'desc': 'A list of default tags to be added to a new post',
    },
    'date_format': {
        'value': "%d %B %Y",
        'desc': 'Short date format for generated HTML',
    },
    'datetime_format': {
        'value': "%d %B %Y %H:%M",
        'desc': 'Full date and time format for generated HTML',
    },
    'deploy_cmd': {
        'value': '',
        'desc': 'Shell command for web content deployment',
    },
    'editor_cmd': {
        'value': "$EDITOR \"\"{source}\"\"",
        'desc': 'Shell command to open files in text editor. {source} will '
                'be replaced with a file path to open',
    },
    'enable_search_form': {
        'value': True,
        'desc': 'Enable Google search form',
    },
    'addthis_id': {
        'value': '',
        'desc': 'AddThis.com identifier, e.g. ra-1234567890123456 (sharing '
                'buttons code will be included if the value is not empty)',
    },
    'disqus_id': {
        'value': '',
        'desc': 'Site short name for Disqus comments (comments code '
                'will be included if the value is not empty)',
    },
    'google_analytics_id': {
        'value': '',
        'desc': 'Google Analytics tracking ID, e.g. UA-12345678-9 (tracking '
                'code will be included if the value is not empty)',
    },
    'index_page': {
        'value': 'index.html',
        'desc': 'File name for an index page',
    },
    'iso_datetime_format': {
        'value': "%d %B %Y",
        'desc': 'ISO date format for generated HTML',
    },
    'humans_author_location': {
        'value': '',
        'desc': 'Site author location for humans.txt',
    },
    'humans_doctype': {
        'value': 'HTML5',
        'desc': 'Site Doctype for humans.txt',
    },
    'humans_ide': {
        'value': 'Netscape Composer 7',
        'desc': 'IDE value for humans.txt',
    },
    'humans_language': {
        'value': 'English',
        'desc': 'Site Language for humans.txt',
    },
    'less_cmd': {
        'value': "lessc --compress {source} > {dest}",
        'desc': 'Shell command for LESS compillation',
    },
    'log_backup_cnt': {
        'value': 3,
        'desc': 'Amount of log files to keep',
    },
    'log_file': {
        'value': 'pub.log',
        'desc': 'Log file name',
    },
    'log_max_size': {
        'value': 1024 * 1024,
        'desc': 'Maximum file size for log rotation (in bytes)',
    },
    'menu': {
        'value': [
            {'title': 'About', 'href': '/about.html'},
            {'title': 'Archive', 'href': '/archive.html'},
        ],
        'desc': 'Navigation menu items',
    },
    'min_css': {
        'value': False,
        'desc': 'Enable CSS minification',
    },
    'min_css_cmd': {
        'value': "yuicompressor --type css -o {dest} {source}",
        'desc': 'Shell command for CSS minification',
    },
    'min_html': {
        'value': False,
        'desc': 'Remove extra whitespace from HTML',
    },
    'min_js': {
        'value': False,
        'desc': 'Enable JavaScript minification',
    },
    'min_js_cmd': {
        'value': "yuicompressor --type js --nomunge -o {dest} {source}",
        'desc': 'Shell command for JavaScript minification',
    },
    'opengraph_enabled': {
        'value': True,
        'desc': 'Include OpenGraph metadata to the page header',
    },
    'page_tpl': {
        'value': 'page',
        'desc': 'Template name for pages',
    },
    'pluso_enabled': {
        'value': False,
        'desc': 'Enable pluso.ru sharing buttons',
    },
    'port': {
        'value': 8000,
        'desc': 'Port number for the local web server',
    },
    'post_at_root_url': {
        'value': True,
        'desc': 'Put a copy of the latest post to the website root',
    },
    'post_location': {
        'value': '{year}/{month}/{day}/{name}.html',
        'desc': 'Post destination path pattern',
    },
    'post_source_name': {
        'value': '{year}{month}{day}-{name}.md',
        'desc': 'Post source file name pattern',
    },
    'post_tpl': {
        'value': 'post',
        'desc': 'Template name for blog posts',
    },
    'rel_root_url': {
        'value': '/',
        'desc': 'Relative root website URL',
    },
    'root_url': {
        'value': 'http://example.com/',
        'desc': 'Root website URL',
    },
    'site_twitter': {
        'value': '',
        'desc': 'Website twitter account',
    },
    'source_url': {
        'value': 'http://github.com/username/example.com',
        'desc': 'Website source URL',
    },
    'subtitle': {
        'value': '',
        'desc': 'Site sublitle',
    },
    'tag_location': {
        'value': 'tags/{tag}.html',
        'desc': 'Tag file name pattern for tag page and URL generation',
    },
    'time_format': {
        'value': ["%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M", "%Y/%m/%d"],
        'desc': 'A list of possible date/time formats for the '
                'post and page header fields',
    },
    'title': {
        'value': 'Brand New Blog',
        'desc': 'Site title',
    },
    'twittercards_enabled': {
        'value': True,
        'desc': 'Include Twitter Cards metadata to the page header',
    },
    'verbose': {
        'value': True,
        'desc': 'Enable verbose logging',
    },
}

# coding: utf-8

# Site configuration file name
CONF_NAME = 'conf.yml'

# Configuration file header
CONF_HEADER = 'public-static configuration file'

# standard name for template content block
CONTENT_BLOCK = 'content'

# default image number limitation for 'image ls' command output
LS_NUM = 10

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

# prototype for the site source directory, located within the package directory
PROTO_DIR = 'prototype'

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

# default post name
UNTITLED_POST = 'untitled-post'

# parameters sequence for the configuration file
EXPORTS = [
    'author',
    'author_url',
    'default_tags',
    'default_templates',
    'deploy_cmd',
    'id_disqus',
    'editor_cmd',
    'enable_search_form',
    'id_addthis',
    'id_google_analytics',
    'image_max_height',
    'image_max_width',
    'images_location',
    'images_path',
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
    'source_url',
    'subtitle',
    'title',
    'verbose',
]

# configuration parameters
DEFAULTS = {
    'archive_location': {
        'value': 'archive/index.html',
        'desc': 'Blog archive page location',
    },
    'assets_path': {
        'value': 'assets',
        'desc': 'Web assets path inside website source dir (*.js, *.css, etc)',
    },
    'atom_location': {
        'value': 'atom.xml',
        'desc': 'Atom feed file name',
    },
    'author': {
        'value': 'Anonymous',
        'desc': 'Author name',
    },
    'author_url': {
        'value': 'http://example.net',
        'desc': 'Author home page',
    },
    'build_path': {
        'value': 'build',
        'desc': 'Build path for web content generator output',
    },
    'default_tags': {
        'value': ['misc'],
        'desc': 'A list of default tags to be added to a new post',
    },
    'default_templates': {
        'value': False,
        'desc': 'Use default templates for all pages',
    },
    'date_format': {
        'value': "%B %d, %Y",
        'desc': 'Page/post short date format for generated HTML',
    },
    'datetime_format': {
        'value': "%B %d, %Y %H:%M",
        'desc': 'Page/post full date and time format for generated HTML',
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
    'id_addthis': {
        'value': '',
        'desc': 'AddThis.com identifier, e.g. ra-1234567890123456 (sharing '
                'buttons code will be included if the value is not empty)',
    },
    'id_disqus': {
        'value': '',
        'desc': 'Site short name for Disqus comments (comments code '
                'will be included if the value is not empty)',
    },
    'id_google_analytics': {
        'value': '',
        'desc': 'Google Analytics tracking ID, e.g. UA-12345678-9 (tracking '
                'code will be included if the value is not empty)',
    },
    'image_max_height': {
        'value': 0,
        'desc': 'Maximum vrtical image size for previews (0 for no limit)',
    },
    'image_max_width': {
        'value': 600,
        'desc': 'Maximum horizontal image size for previews (0 for no limit)',
    },
    'images_location': {
        'value': 'img',
        'desc': 'Path to image files inside build directory',
    },
    'images_path': {
        'value': 'images',
        'desc': 'Image files path inside website source dir',
    },
    'index_page': {
        'value': 'index.html',
        'desc': 'File name for an index page',
    },
    'iso_datetime_format': {
        'value': "%B %d, %Y",
        'desc': 'Page/post short date format for generated HTML',
    },
    'humans_author_location': {
        'value': '',
        'desc': 'Site author location for humans.txt',
    },
    'humans_author_twitter': {
        'value': '',
        'desc': 'Site author twitter account for humans.txt',
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
        'value': "lessc --yui-compress {source} > {dest}",
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
            {'title': 'Archive', 'href': '/archive/'},
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
    'page_tpl': {
        'value': 'page',
        'desc': 'Template name for pages',
    },
    'pages_path': {
        'value': 'pages',
        'desc': 'Page files path inside website source dir',
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
    'posts_path': {
        'value': 'posts',
        'desc': 'Post files path inside website source dir',
    },
    'rel_root_url': {
        'value': '/',
        'desc': 'Relative root website URL',
    },
    'root_url': {
        'value': 'http://example.com/',
        'desc': 'Root website URL',
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
    'verbose': {
        'value': True,
        'desc': 'Enable verbose logging',
    },
}

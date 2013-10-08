# coding: utf-8

# Site configuration file name
CONF_NAME = 'conf.yaml'

# Configuration file header
CONF_HEADER = """public-static configuration file"""

# Program name and version info
GENERATOR = "public-static"

# Program home page
GENERATOR_URL = 'http://github.com/dreikanter/public-static'

# Logger message format
LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"

# Logger message timestamp format
LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

# generic site directory name within the package directory
GENERIC_DIR = 'generic-site'

# crash log file name
DUMP_FILE = 'crash.log'

# templates directory name
TEMPLATES_DIR = 'templates'

# source file types
ASSET_TYPE = 'asset'
POST_TYPE = 'post'
PAGE_TYPE = 'page'

BROWSER_DELAY = 2.0

# default post name
UNTITLED_POST = 'untitled-post'

# environment variable name to override 'verbose' configuration parameter
ENV_VERBOSE = 'ps_verbose'

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

# images metadata file
IMAGES_INDEX = 'images.yaml'

# standard name for template content block
MAIN_BLOCK = 'main'

# parameters sequence for the configuration file
EXPORTS = [
    'title',
    'subtitle',
    'author',
    'author_url',
    'root_url',
    'source_url',
    'post_location',
    'port',
    'min_js',
    'min_css',
    'min_html',
    'min_js_cmd',
    'min_css_cmd',
    'less_cmd',
    'deploy_cmd',
    'editor_cmd',
    'default_tags',
    'verbose',
    'menu',
    'enable_search_form',
    'google_analytics_tracking_id',
    'disqus_short_name',
    'addthis_id',
    'pluso_enabled',
]

# configuration parameters
DEFAULTS = {
    'title': {
        'value': 'Untitled Blog',
        'desc': 'Site title',
    },
    'subtitle': {
        'value': '',
        'desc': 'Site sublitle',
    },
    'author': {
        'value': 'Anonymous',
        'desc': 'Author name',
    },
    'author_url': {
        'value': 'http://example.net',
        'desc': 'Author home page',
    },
    'root_url': {
        'value': 'http://example.com/',
        'desc': 'Root website URL',
    },
    'rel_root_url': {
        'value': '/',
        'desc': 'Relative root website URL',
    },
    'source_url': {
        'value': 'http://github.com/username/example.com',
        'desc': 'Website source URL',
    },
    'build_path': {
        'value': 'build',
        'desc': 'Build path for web content generator output',
    },
    'pages_path': {
        'value': 'pages',
        'desc': 'Page files path inside website source dir',
    },
    'posts_path': {
        'value': 'posts',
        'desc': 'Post files path inside website source dir',
    },
    'assets_path': {
        'value': 'assets',
        'desc': 'Web assets path inside website source dir (*.js, *.css, etc)',
    },
    'tpl_path': {
        'value': TEMPLATES_DIR,
        'desc': 'Relative path to the templates directory inside '
                'website source dir',
    },
    'images_path': {
        'value': 'images',
        'desc': 'Image files path inside website source dir',
    },
    'post_location': {
        'value': '{year}/{month}/{day}/{name}.html',
        'desc': 'Post destination path pattern',
    },
    'post_source_name': {
        'value': '{year}{month}{day}-{name}.md',
        'desc': 'Post source file name pattern',
    },
    'port': {
        'value': 8000,
        'desc': 'Port number for the local web server',
    },
    'page_tpl': {
        'value': 'page',
        'desc': 'Template name for pages',
    },
    'post_tpl': {
        'value': 'post',
        'desc': 'Template name for blog posts',
    },
    'min_js': {
        'value': False,
        'desc': 'Enable JavaScript minification',
    },
    'min_css': {
        'value': False,
        'desc': 'Enable CSS minification',
    },
    'min_html': {
        'value': False,
        'desc': 'Remove extra whitespace from HTML.',
    },
    'min_js_cmd': {
        'value': "yuicompressor --type js --nomunge -o {dest} {source}",
        'desc': 'Shell command for JavaScript minification',
    },
    'min_css_cmd': {
        'value': "yuicompressor --type css -o {dest} {source}",
        'desc': 'Shell command for CSS minification',
    },
    'less_cmd': {
        'value': "lessc --yui-compress {source} > {dest}",
        'desc': 'Shell command for LESS compillation',
    },
    'deploy_cmd': {
        'value': '',
        'desc': 'Shell command for web content deployment',
    },
    'editor_cmd': {
        'value': "$EDITOR \"\"{source}\"\"",
        'desc': 'Shell command to open files in text editor. {source} will '
                'be replaced with a file path to open.',
    },
    'index_page': {
        'value': 'index.html',
        'desc': 'File name for an index page',
    },
    'atom_location': {
        'value': 'atom.xml',
        'desc': 'Atom feed file name.',
    },
    'post_at_root_url': {
        'value': True,
        'desc': 'Put a copy of the latest post to the website root',
    },
    'default_tags': {
        'value': ['misc'],
        'desc': 'A list of default tags to be added to a new post',
    },
    'log_file': {
        'value': 'pub.log',
        'desc': 'Log file name',
    },
    'log_max_size': {
        'value': 1024 * 1024,
        'desc': 'Maximum file size for log rotation (in bytes)',
    },
    'log_backup_cnt': {
        'value': 3,
        'desc': 'Amount of log files to keep',
    },
    'verbose': {
        'value': True,
        'desc': 'Enable verbose logging',
    },
    'time_format': {
        'value': ['%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M', '%Y/%m/%d'],
        'desc': 'A list of possible date/time formats for the '
                'post and page header fields',
    },
    'datetime_format': {
        'value': '%B %d, %Y %H:%M',
        'desc': 'Page/post full date and time format for generated HTML',
    },
    'date_format': {
        'value': '%B %d, %Y',
        'desc': 'Page/post short date format for generated HTML',
    },
    'iso_datetime_format': {
        'value': '%B %d, %Y',
        'desc': 'Page/post short date format for generated HTML',
    },
    'menu': {
        'value': [
            {'title': 'About', 'href': '/about.html'},
            {'title': 'Archive', 'href': '/archive/'},
        ],
        'desc': 'Navigation menu items',
    },
    'enable_search_form': {
        'value': True,
        'desc': 'Enable Google search form',
    },
    'humans_language': {
        'value': 'English',
        'desc': 'Site Language for humans.txt',
    },
    'humans_doctype': {
        'value': 'HTML5',
        'desc': 'Site Doctype for humans.txt',
    },
    'humans_ide': {
        'value': 'Netscape Composer 7',
        'desc': 'IDE value for humans.txt',
    },
    'humans_author_twitter': {
        'value': '',
        'desc': 'Site author twitter account for humans.txt',
    },
    'humans_author_location': {
        'value': '',
        'desc': 'Site author location for humans.txt',
    },
    'tag_location': {
        'value': 'tags/{tag}.html',
        'desc': 'Tag file name pattern for tag page and URL generation',
    },
    'archive_location': {
        'value': 'archive/index.html',
        'desc': 'Blog archive page location.',
    },
    'google_analytics_tracking_id': {
        'value': '',
        'desc': 'Google Analytics tracking ID, e.g. UA-12345678-9 (tracking '
                'code will be included if the value is not empty)',
    },
    'disqus_short_name': {
        'value': '',
        'desc': 'Site short name for Disqus comments (comments code '
                'will be included if the value is not empty)',
    },
    'addthis_id': {
        'value': '',
        'desc': 'AddThis.com identifier, e.g. ra-1234567890123456 (sharing '
                'buttons code will be included if the value is not empty)',
    },
    'images_location': {
        'value': 'img',
        'desc': 'Path to image files inside build directory',
    },
    'pluso_enabled': {
        'value': False,
        'desc': 'Enable pluso.ru sharing buttons',
    },
}

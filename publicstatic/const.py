# coding: utf-8

from publicstatic.version import get_version


# Site configuration file name
CONF_NAME = 'conf.yaml'

# Configuration file header
CONF_HEADER = """public-static configuration file"""

# Program name and version info
GENERATOR = "public-static {version}".format(version=get_version())

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

# prototypes directory name
PROTO_DIR = 'prototypes'

# source file types
ASSET_TYPE = 'asset'
POST_TYPE = 'post'
PAGE_TYPE = 'page'

BROWSER_DELAY = 2.0

# default post name
UNTITLED_POST = 'untitled-post'

# environment variable name to override 'verbose' configuration parameter
ENV_VERBOSE = 'ps_verbose'

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
    'min_js_cmd',
    'min_css_cmd',
    'less_cmd',
    'deploy_cmd',
    'editor_cmd',
    'default_tags',
    'verbose',
    'menu',
    'enable_search_form',
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
    'prototypes_path': {
        'value': PROTO_DIR,
        'desc': 'Relative path to the prototypes directory inside '
                'website source dir',
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
        'value': 'default-page',
        'desc': 'Template name for pages',
    },
    'post_tpl': {
        'value': 'default-post',
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
    'markdown_extensions': {
        'value': ['nl2br', 'grid', 'smartypants'],
        'desc': 'A list of markdown processor extensions',
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
        'value': ['%Y/%m/%d %H:%M:%S', '%Y/%m/%d'],
        'desc': 'A list of possible date/time formats for the '
                ' post and page header fields',
    },
    'page_datetime_format': {
        'value': '%Y/%m/%d %H:%M',
        'desc': 'Page/post full date and time format for generated HTML',
    },
    'page_date_format': {
        'value': '%Y/%m/%d',
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
    }

}

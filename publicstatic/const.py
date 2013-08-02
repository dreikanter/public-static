# coding: utf-8

import os
import re
from publicstatic.version import get_version


# Site configuration file name
CONF_NAME = 'pub.conf'

# Program name and version info
GENERATOR = "public-static {version}".format(version=get_version())

# Logger message format
LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"

# Logger message timestamp format
LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

GENERIC_PATH = 'generic-site'

GENERIC_PAGES = 'generic-pages'

DUMP_FILE = 'crash.log'

TEMPLATES_DIR = 'templates'

PROTO_DIR = 'prototypes'

ASSET_TYPE = 'asset'
POST_TYPE = 'post'
PAGE_TYPE = 'page'

BROWSER_DELAY = 2.0

DEFAULTS = [
    {
        'name': 'title',
        'value': 'Untitled Blog',
        'desc': 'Site title',
        'export': True,
    },
    {
        'name': 'subtitle',
        'value': '',
        'desc': 'Site sublitle',
        'export': True,
    },
    {
        'name': 'author',
        'value': 'Anonymous',
        'desc': 'Author name',
        'export': True,
    },
    {
        'name': 'author_url',
        'value': 'http://example.net',
        'desc': 'Author home page',
        'export': True,
    },
    {
        'name': 'root_url',
        'value': 'http://example.com/',
        'desc': 'Root website URL',
        'export': True,
    },
    {
        'name': 'rel_root_url',
        'value': '/',
        'desc': 'Relative root website URL',
        'export': False,
    },
    {
        'name': 'source_url',
        'value': 'http://github.com/username/example.com',
        'desc': 'Website source URL',
        'export': True,
    },
    {
        'name': 'build_path',
        'value': 'www',
        'desc': 'Build path for web content generator output',
        'export': False,
    },
    {
        'name': 'pages_path',
        'value': 'pages',
        'desc': 'Page files path inside website source dir',
        'export': False,
    },
    {
        'name': 'posts_path',
        'value': 'posts',
        'desc': 'Post files path inside website source dir',
        'export': False,
    },
    {
        'name': 'assets_path',
        'value': 'assets',
        'desc': 'Web assets path inside website source dir (*.js, *.css, etc)',
        'export': False,
    },
    {
        'name': 'tpl_path',
        'value': TEMPLATES_DIR,
        'desc': 'Relative path to the templates directory inside ' \
                'website source dir',
        'export': False,
    },
    {
        'name': 'prototypes_path',
        'value': PROTO_DIR,
        'desc': 'Relative path to the prototypes directory inside ' \
                'website source dir',
        'export': False,
    },
    {
        'name': 'post_location',
        'value': '{year}/{month}/{day}/{name}.html',
        'desc': 'Post file name pattern',
        'export': True,
    },
    {
        'name': 'port',
        'value': 8000,
        'desc': 'Port number for the local web server',
        'export': True,
    },
    {
        'name': 'page_tpl',
        'value': 'default-page',
        'desc': 'Template name for pages',
        'export': False,
    },
    {
        'name': 'post_tpl',
        'value': 'default-post',
        'desc': 'Template name for blog posts',
        'export': False,
    },
    {
        'name': 'min_js',
        'value': True,
        'desc': 'Enable JavaScript minification',
        'export': True,
    },
    {
        'name': 'min_css',
        'value': True,
        'desc': 'Enable CSS minification',
        'export': True,
    },
    {
        'name': 'min_less',
        'value': True,
        'desc': 'Apply CSS minimization tool to the LESS processor output',
        'export': True,
    },
    {
        'name': 'min_js_cmd',
        'value': "yuicompressor --type js --nomunge -o {dest} {source}",
        'desc': 'Shell command for JavaScript minification',
        'export': True,
    },
    {
        'name': 'min_css_cmd',
        'value': "yuicompressor --type css -o {dest} {source}",
        'desc': 'Shell command for CSS minification',
        'export': True,
    },
    {
        'name': 'less_cmd',
        'value': "dotless {source} {dest}",
        'desc': 'Shell command for LESS compillation',
        'export': True,
    },
    {
        'name': 'deploy_cmd',
        'value': '',
        'desc': 'Shell command for web content deployment',
        'export': True,
    },
    {
        'name': 'editor_cmd',
        'value': "$EDITOR \"\"{source}\"\"",
        'desc': 'Shell command to open files in text editor. {source} will ' \
                'be replaced with a file path to open.',
        'export': True,
    },
    {
        'name': 'markdown_extensions',
        'value': ['nl2br', 'grid', 'smartypants'],
        'desc': 'A list of markdown processor extensions',
        'export': False,
    },
    {
        'name': 'index_page',
        'value': 'index.html',
        'desc': 'File name for an index page',
        'export': False,
    },
    {
        'name': 'archive_page',
        'value': 'archive.html',
        'desc': 'File name for an archive page',
        'export': False,
    },
    {
        'name': 'atom_feed',
        'value': 'feed.atom',
        'desc': 'Atom feed file name.',
        'export': False,
    },
    {
        'name': 'post_at_root_url',
        'value': True,
        'desc': 'Put a copy of the latest post to the website root',
        'export': False,
    },
    {
        'name': 'default_tags',
        'value': [ 'misc' ],
        'desc': 'A list of default tags to be added to a new post',
        'export': True,
    },
    {
        'name': 'log_file',
        'value': 'pub.log',
        'desc': 'Log file name',
        'export': False,
    },
    {
        'name': 'log_max_size',
        'value': 1024 * 1024,
        'desc': 'Maximum file size for log rotation (in bytes)',
        'export': False,
    },
    {
        'name': 'log_backup_cnt',
        'value': 3,
        'desc': 'Amount of log files to keep',
        'export': False,
    },
    {
        'name': 'verbose',
        'value': False,
        'desc': 'Enable verbose logging',
        'export': True,
    },
    {
        'name': 'time_format',
        'value': [ '%Y/%m/%d %H:%M:%S', '%Y/%m/%d' ],
        'desc': 'A list of possible date/time formats for the ' \
                ' post and page header fields',
        'export': False,
    },
    {
        'name': 'page_datetime_format',
        'value': '%Y/%m/%d %H:%M',
        'desc': 'Page/post full date and time format for generated HTML',
        'export': False,
    },
    {
        'name': 'page_date_format',
        'value': '%Y/%m/%d',
        'desc': 'Page/post short date format for generated HTML',
        'export': False,
    },
    {
        'name': 'menu',
        'value': [
            { 'title': 'About', 'href': '/about.html' },
            { 'title': 'Archive', 'href': '/archive.html' },
        ],
        'desc': 'Navigation menu items',
        'export': True,
    },
    {
        'name': 'enable_search_form',
        'value': True,
        'desc': 'Enable Google search form',
        'export': True,
    },
]

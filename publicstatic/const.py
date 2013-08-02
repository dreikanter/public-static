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

DEFAULTS = [
    {
        'name': 'title',
        'value': 'Untitled Blog',
        'desc': 'Site title',
    },
    {
        'name': 'subtitle',
        'value': '',
        'desc': 'Site sublitle',
    },
    {
        'name': 'author',
        'value': 'Anonymous',
        'desc': 'Author name',
    },
    {
        'name': 'author_url',
        'value': 'http://example.net',
        'desc': 'Author home page',
    },
    {
        'name': 'build_path',
        'value': 'www',
        'desc': 'Build path for web content generator output',
    },
    {
        'name': 'pages_path',
        'value': 'pages',
        'desc': 'Page files path inside website source dir',
    },
    {
        'name': 'posts_path',
        'value': 'posts',
        'desc': 'Post files path inside website source dir',
    },
    {
        'name': 'assets_path',
        'value': 'assets',
        'desc': 'Web assets path inside website source dir (*.js, *.css, etc)',
    },
    {
        'name': 'tpl_path',
        'value': TEMPLATES_DIR,
        'desc': 'Relative path to the templates directory inside ' \
                'website source dir',
    },
    {
        'name': 'prototypes_path',
        'value': PROTO_DIR,
        'desc': 'Relative path to the prototypes directory inside ' \
                'website source dir',
    },
    {
        'name': 'root_url',
        'value': 'http://example.com/',
        'desc': 'Root website URL',
    },
    {
        'name': 'rel_root_url',
        'value': '/',
        'desc': 'Relative root website URL',
    },
    {
        'name': 'source_url',
        'value': 'http://github.com/username/example.com',
        'desc': 'Website source URL',
    },
    {
        'name': 'post_location',
        'value': '{year}/{month}/{day}/{name}.html',
        'desc': 'Post file name pattern',
    },
    {
        'name': 'port',
        'value': 8000,
        'desc': 'Port number for the local web server',
    },
    {
        'name': 'browser_delay',
        'value': 2.0,
        'desc': '',
    },
    {
        'name': 'page_tpl',
        'value': 'default-page',
        'desc': 'Template name for pages',
    },
    {
        'name': 'post_tpl',
        'value': 'default-post',
        'desc': 'Template name for blog posts',
    },
    {
        'name': 'min_js',
        'value': True,
        'desc': 'Enable JavaScript minification',
    },
    {
        'name': 'min_css',
        'value': True,
        'desc': 'Enable CSS minification',
    },
    {
        'name': 'min_less',
        'value': True,
        'desc': 'Apply CSS minimization tool to the LESS processor output',
    },
    {
        'name': 'min_js_cmd',
        'value': "yuicompressor --type js --nomunge -o {dest} {source}",
        'desc': 'Shell command for JavaScript minification',
    },
    {
        'name': 'min_css_cmd',
        'value': "yuicompressor --type css -o {dest} {source}",
        'desc': 'Shell command for CSS minification',
    },
    {
        'name': 'less_cmd',
        'value': "dotless {source} {dest}",
        'desc': 'Shell command for LESS compillation',
    },
    {
        'name': 'deploy_cmd',
        'value': '',
        'desc': 'Shell command for web content deployment',
    },
    {
        'name': 'editor_cmd',
        'value': "$EDITOR \"{source}\"",
        'desc': 'Shell command to open files in text editor. {source} will ' \
                'be replaced with a file path to open.',
    },
    {
        'name': 'markdown_extensions',
        'value': ['nl2br', 'grid', 'smartypants'],
        'desc': 'A list of markdown processor extensions',
    },
    {
        'name': 'index_page',
        'value': 'index.html',
        'desc': 'File name for an index page',
    },
    {
        'name': 'archive_page',
        'value': 'archive.html',
        'desc': 'File name for an archive page',
    },
    {
        'name': 'archive_page_title',
        'value': 'Archive',
        'desc': '',
    },
    {
        'name': 'atom_feed',
        'value': 'feed.atom',
        'desc': 'Atom feed file name.',
    },
    {
        'name': 'post_at_root_url',
        'value': True,
        'desc': 'Put a copy of the latest post to the website root',
    },
    {
        'name': 'default_tags',
        'value': [ 'misc' ],
        'desc': 'A list of default tags to be added to a new post',
    },
    {
        'name': 'log_file',
        'value': 'pub.log',
        'desc': 'Log file name',
    },
    {
        'name': 'log_max_size',
        'value': 1024 * 1024,
        'desc': 'Maximum file size for log rotation (in bytes)',
    },
    {
        'name': 'log_backup_cnt',
        'value': 3,
        'desc': 'Amount of log files to keep',
    },
    {
        'name': 'verbose',
        'value': False,
        'desc': 'Enable verbose logging',
    },
    {
        'name': 'time_format',
        'value': [ '%Y/%m/%d %H:%M:%S', '%Y/%m/%d' ],
        'desc': 'A list of possible date/time formats for the ' \
                ' post and page header fields',
    },
    {
        'name': 'page_datetime_format',
        'value': '%Y/%m/%d %H:%M',
        'desc': 'Page/post full date and time format for generated HTML',
    },
    {
        'name': 'page_date_format',
        'value': '%Y/%m/%d',
        'desc': 'Page/post short date format for generated HTML',
    },
    {
        'name': 'menu',
        'value': [
            { 'title': 'About', 'href': '/about.html' },
            { 'title': 'Archive', 'href': '/archive.html' },
        ],
        'desc': 'Navigation menu items',
    },
    {
        'name': 'enable_search_form',
        'value': True,
        'desc': 'Enable Google search form',
    },
]

# coding: utf-8

import os
import re
from publicstatic.version import get_version


CONF_NAME = 'pub.conf'
GENERATOR = "public-static {version}".format(version=get_version())

CONSOLE_FMT = "%(asctime)s %(levelname)s: %(message)s"
CONSOLE_DATE_FMT = "%H:%M:%S"
FILE_FMT = "%(asctime)s %(levelname)s: %(message)s"
FILE_DATE_FMT = "%Y/%m/%d %H:%M:%S"

GENERIC_PATH = 'generic-site'
GENERIC_PAGES = 'generic-pages'
FEED_DIR = 'feed'

RE_FLAGS = re.I | re.M | re.U
H1_PATTERN = re.compile(r"^\s*#\s*(.*)\s*", RE_FLAGS)
POST_PATTERN = re.compile(r"[\w\\/]+")
URI_SEP_PATTERN = re.compile(r"[^a-z\d\%s]+" % os.sep, RE_FLAGS)
URI_EXCLUDE_PATTERN = re.compile(r"[,.`\'\"\!@\#\$\%\^\&\*\(\)\+]+", RE_FLAGS)
PARAM_PATTERN = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", RE_FLAGS)

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
        'desc': '',
    },
    {
        'name': 'pages_path',
        'value': 'pages',
        'desc': '',
    },
    {
        'name': 'posts_path',
        'value': 'posts',
        'desc': '',
    },
    {
        'name': 'assets_path',
        'value': 'assets',
        'desc': '',
    },
    {
        'name': 'tpl_path',
        'value': 'templates',
        'desc': '',
    },
    {
        'name': 'prototypes_path',
        'value': 'prototypes',
        'desc': '',
    },
    {
        'name': 'rel_root_url',
        'value': '/',
        'desc': '',
    },
    {
        'name': 'root_url',
        'value': 'http://example.com/',
        'desc': '',
    },
    {
        'name': 'source_url',
        'value': 'http://github.com/username/example.com',
        'desc': 'Website source URL',
    },
    {
        'name': 'post_location',
        'value': '{year}/{month}/{day}/{name}.html',
        'desc': '',
    },
    {
        'name': 'port',
        'value': 8000,
        'desc': '',
    },
    {
        'name': 'browser_delay',
        'value': 2.0,
        'desc': '',
    },
    {
        'name': 'page_tpl',
        'value': 'default-page',
        'desc': '',
    },
    {
        'name': 'post_tpl',
        'value': 'default-post',
        'desc': '',
    },
    {
        'name': 'min_js',
        'value': True,
        'desc': '',
    },
    {
        'name': 'min_css',
        'value': True,
        'desc': '',
    },
    {
        'name': 'min_less',
        'value': True,
        'desc': 'Apply CSS minimization tool to the LESS processor output',
    },
    {
        'name': 'min_js_cmd',
        'value': "yuicompressor --type js --nomunge -o {dest} {source}",
        'desc': '',
    },
    {
        'name': 'min_css_cmd',
        'value': "yuicompressor --type css -o {dest} {source}",
        'desc': '',
    },
    {
        'name': 'deploy_cmd',
        'value': '',
        'desc': '',
    },
    {
        'name': 'less_cmd',
        'value': "dotless {source} {dest}",
        'desc': '',
    },
    {
        'name': 'editor_cmd',
        'value': "$EDITOR \"{source}\"",
        'desc': '',
    },
    {
        'name': 'markdown_extensions',
        'value': ['nl2br', 'grid', 'smartypants'],
        'desc': '',
    },
    {
        'name': 'index_page',
        'value': 'index.html',
        'desc': '',
    },
    {
        'name': 'archive_page',
        'value': 'archive.html',
        'desc': '',
    },
    {
        'name': 'archive_page_title',
        'value': 'Archive',
        'desc': '',
    },
    {
        'name': 'atom_feed',
        'value': 'feed.atom',
        'desc': '',
    },
    {
        'name': 'post_at_root_url',
        'value': True,
        'desc': 'Put a copy of the latest post to the website root',
    },
    {
        'name': 'default_tags',
        'value': [ 'misc' ],
        'desc': '',
    },
    {
        'name': 'log_file',
        'value': 'pub.log',
        'desc': '',
    },
    {
        'name': 'log_max_size',
        'value': 1024 * 1024,
        'desc': '',
    },
    {
        'name': 'log_backup_cnt',
        'value': 3,
        'desc': '',
    },
    {
        'name': 'verbose',
        'value': False,
        'desc': 'Verbose output',
    },
    {
        'name': 'time_format',
        'value': [ '%Y/%m/%d %H:%M:%S', '%Y/%m/%d' ],
        'desc': 'Possible date and time formats for the page header fields',
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
        'desc': '',
    },
    {
        'name': 'enable_search_form',
        'value': True,
        'desc': 'Enable Google search form',
    },
]

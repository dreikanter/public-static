# coding: utf-8

import os
import re

CONF_NAME = 'pub.conf'
GENERATOR = "public-static {version}"

CONSOLE_FMT = "%(asctime)s %(levelname)s: %(message)s"
CONSOLE_DATE_FMT = "%H:%M:%S"
FILE_FMT = "%(asctime)s %(levelname)s: %(message)s"
FILE_DATE_FMT = "%Y/%m/%d %H:%M:%S"
TIME_FMT = "%Y/%m/%d %H:%M:%S"

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
        'value': '',
        'desc': 'Author name',
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
        'desc': '',
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
        'value': "lessc -x {source} > {dest}",
        'desc': '',
    },
    {
        'name': 'markdown_extensions',
        'value': ['nl2br', 'grid', 'smartypants'],
        'desc': '',
    },
    {
        'name': 'editor_cmd',
        'value': "$EDITOR \"{source}\"",
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
        'desc': '',
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
        'desc': '',
    },
    {
        'name': 'menu',
        'value': [
            { 'title': 'About', 'href': '/about.html' },
            { 'title': 'Archive', 'href': '/archive.html' },
        ],
        'desc': '',
    },
]


# # See the docs for parameters description
# DEFAULTS = [
#     ('title', 'Untitled Blog'),
#     ('subtitle', ''),
#     ('author', ''),
#     ('generator', "public-static {version}"),
#     ('build_path', 'www'),
#     ('pages_path', 'pages'),
#     ('posts_path', 'posts'),
#     ('assets_path', 'assets'),
#     ('tpl_path', 'templates'),
#     ('prototypes_path', 'prototypes'),
#     ('rel_root_url', '/'),
#     ('root_url', 'http://example.com/'),
#     ('post_location', '{year}/{month}/{day}/{name}.html'),
#     ('port', 8000),
#     ('browser_delay', 2.0),
#     ('page_tpl', 'default-page'),
#     ('post_tpl', 'default-post'),
#     ('min_js', True),
#     ('min_css', True),
#     ('min_less', True),
#     ('min_js_cmd', "yuicompressor --type js --nomunge -o {dest} {source}"),
#     ('min_css_cmd', "yuicompressor --type css -o {dest} {source}"),
#     ('deploy_cmd', ''),
#     ('less_cmd', "lessc -x {source} > {dest}"),
#     ('markdown_extensions', ['nl2br', 'grid', 'smartypants']),
#     ('editor_cmd', "$EDITOR \"{source}\""),
#     ('index_page', 'index.html'),
#     ('archive_page', 'archive.html'),
#     ('archive_page_title', 'Archive'),
#     ('atom_feed', 'feed.atom'),
#     ('post_at_root_url', True),
#     ('menu', [
#         { 'title': 'About', 'href': '/about.html' },
#         { 'title': 'Archive', 'href': '/archive.html' },
#         ]),
#     ('default_tags', [ 'misc' ]),
#     ('log_file', 'pub.log'),
#     ('log_max_size', 1024 * 1024),
#     ('log_backup_cnt', 3),
#     ('verbose', False),
# ]

# coding: utf-8

import os
import re

CONF_NAME = 'pub.conf'

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

# See the docs for parameters description
DEFAULTS = [
    ('title', 'Untitled Blog'),
    ('subtitle', ''),
    ('author', ''),
    ('generator', "public-static {version}"),
    ('build_path', 'www'),
    ('pages_path', 'pages'),
    ('posts_path', 'posts'),
    ('assets_path', 'assets'),
    ('tpl_path', 'templates'),
    ('prototypes_path', 'prototypes'),
    ('rel_root_url', '/'),
    ('root_url', 'http://example.com/'),
    ('post_location', '{year}/{month}/{day}/{name}.html'),
    ('port', 8000),
    ('browser_delay', 2.0),
    ('page_tpl', 'default-page'),
    ('post_tpl', 'default-post'),
    ('min_js', True),
    ('min_css', True),
    ('min_less', True),
    ('min_js_cmd', "yuicompressor --type js --nomunge -o {dest} {source}"),
    ('min_css_cmd', "yuicompressor --type css -o {dest} {source}"),
    ('sync_cmd', ''),
    ('less_cmd', "lessc -x {source} > {dest}"),
    ('markdown_extensions', ['nl2br', 'grid', 'smartypants']),
    ('editor_cmd', "$EDITOR \"{source}\""),
    ('log_file', 'pub.log'),
    ('log_max_size', 0),
    ('log_backup_cnt', 0),
    ('index_page', 'index.html'),
    ('archive_page', 'archive.html'),
    ('atom_feed', 'feed.atom'),
    ('post_at_root_url', True),
    ('menu', [
        { 'title': 'About', 'href': '/about.html' },
        { 'title': 'Archive', 'href': '/archive.html' },
        ])
]

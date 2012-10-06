import codecs
import logging
from logging.handlers import RotatingFileHandler as RFH
import os
import yaml

import authoring

CONF_NAME = 'pub.conf'

CONSOLE_FMT = "%(asctime)s %(levelname)s: %(message)s"
CONSOLE_DATE_FMT = "%H:%M:%S"
FILE_FMT = "%(asctime)s %(levelname)s: %(message)s"
FILE_DATE_FMT = "%Y/%m/%d %H:%M:%S"
TIME_FMT = "%Y/%m/%d %H:%M:%S"

# See the docs for parameters description
DEFAULTS = [
    ('title', ''),
    ('subtitle', ''),
    ('author', ''),
    ('generator', "public-static {version}"),
    ('build_path', 'www'),
    ('pages_path', 'pages'),
    ('posts_path', 'posts'),
    ('assets_path', 'assets'),
    ('tpl_path', 'templates'),
    # ('post_name', '{date}-{name}.md'),
    ('post_url', '{year}/{month}/{day}/{name}.html'),
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
    ('max_size', 0),
    ('backup_cnt', 0),
]

_params = {}  # Configuration parameters

_path = ''  # Configuration file absolute path

_logger = None


def init(args, use_defaults=False):
    """Initializes configuration and logging from Baker arguments"""
    global _path
    _path = os.path.abspath(os.path.join(args.source or '.', CONF_NAME))

    params = dict(DEFAULTS)

    if not use_defaults:  # Reads configuration file and override defaults
        with codecs.open(_path, mode='r', encoding='utf8') as f:
            loaded = yaml.load(f.read())
        loaded = dict((item, loaded[item]) for item in loaded)
        params.update(loaded)

    global _params
    _params = _purify(params)

    global _logger
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)

    level = logging.DEBUG if args.verbose else logging.INFO

    channel = logging.StreamHandler()
    channel.setLevel(level)
    fmt = logging.Formatter(CONSOLE_FMT, CONSOLE_DATE_FMT)
    channel.setFormatter(fmt)
    _logger.addHandler(channel)

    log_file = args.log
    if log_file:
        path = os.path.dirname(log_file)
        if not os.path.isdir(path):
            os.makedirs(path)

        max_size = get('max_size')
        backup_cnt = get('backup_cnt')

        channel = RFH(log_file, maxBytes=max_size, backupCount=backup_cnt)
        channel.setLevel(logging.DEBUG)
        fmt = logging.Formatter(FILE_FMT, FILE_DATE_FMT)
        channel.setFormatter(fmt)
        _logger.addHandler(channel)


def get(param):
    """Returns a single configuration parameter"""
    try:
        return _params[param]
    except KeyError:
        raise Exception('Unknown configuration parameter')
    except TypeError:
        raise Exception('Configuration was not initialized')


def get_logger():
    """Configures and returns root logger"""
    _check(_logger)
    return _logger


def get_path():
    _check(_path)
    return _path


def write_defaults():
    """Write default configuration to specified file"""
    _check(_path)
    f = lambda x: yaml.dump({x[0]: x[1]},
                            width=80,
                            indent=4,
                            default_flow_style=False)
    text = ''.join([f(x) for x in DEFAULTS])
    with codecs.open(_path, mode='w', encoding='utf8') as f:
        f.write(text)


def _check(value):
    if not value:
        raise Exception('Configuration was not initialized')


def _purify(params):
    """Preprocess configuration parameters"""
    gen = params['generator'].strip()
    params['generator'] = gen.format(version=authoring.VERSION)

    params['pages_path'] = _expand(params['pages_path'])
    params['posts_path'] = _expand(params['posts_path'])
    params['assets_path'] = _expand(params['assets_path'])
    params['build_path'] = _expand(params['build_path'])
    params['tpl_path'] = _expand(params['tpl_path'])

    params['min_js_cmd'] = params['min_js_cmd'].strip()
    params['min_css_cmd'] = params['min_css_cmd'].strip()
    params['sync_cmd'] = params['sync_cmd'].strip()

    params['browser_delay'] = float(params['browser_delay'])
    params['port'] = int(params['port'])

    return params


def _expand(rel_path):
    """Expands relative path using configuration file location as base
    directory. Absolute pathes will be returned as is."""
    if not os.path.isabs(rel_path):
        base = os.path.dirname(os.path.abspath(_path))
        rel_path = os.path.join(base, rel_path)
    return rel_path

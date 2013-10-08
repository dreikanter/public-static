# coding: utf-8

"""Configuration-related fuctionality and defaults."""

import codecs
from datetime import datetime
import os
import yaml
from publicstatic import authoring
from publicstatic import const
from publicstatic import errors
from publicstatic import version

_params = {}  # Configuration parameters
_path = ''  # Configuration file absolute path


class NotFoundException(errors.BasicException):
    """configuration file not found"""
    pass


class ParsingError(errors.BasicException):
    """error reading configuration file"""
    pass


class DirectoryExistsException(errors.BasicException):
    """directory already exists"""
    pass


class NotInitializedException(errors.BasicException):
    """configuration was not initialized"""
    pass


def defaults():
    """Returns default configuration."""
    return {key: value['value'] for key, value in const.DEFAULTS.items()}


def load(conf_path):
    """Initializes configuration."""
    global _path
    _path = find_conf(conf_path or '.')

    if not _path:
        raise NotFoundException()

    try:
        with codecs.open(_path, mode='r', encoding='utf-8') as f:
            loaded = yaml.load(f.read())
    except (IOError, OSError, yaml.scanner.ScannerError) as ex:
        raise ParsingError(error=str(ex)) from ex

    global _params
    _params = defaults()
    _params.update(dict((item, loaded[item]) for item in loaded))
    _params = _purify(_params)


def generate(conf_path):
    """Generates new configuration file using defaults."""
    global _path
    _path = os.path.join(os.path.abspath(conf_path), const.CONF_NAME)

    if os.path.isdir(site_dir()):
        raise DirectoryExistsException(path=site_dir())
    else:
        os.makedirs(site_dir())

    header = "# %s\n\n" % const.CONF_HEADER
    exports = [opt for opt in const.DEFAULTS.keys() if opt in const.EXPORTS]
    text = '\n'.join([_dumpopt(opt) for opt in exports])
    with codecs.open(_path, mode='w', encoding='utf-8') as f:
        f.write(header + text)

    global _params
    _params = _purify(defaults())


def find_conf(conf_path):
    """Walks from the specified directory path up to the root until
    configuration file will be found. Returns full configuration file path
    or None if there are no one."""
    path = os.path.abspath(conf_path).rstrip(os.path.sep + os.path.altsep)
    last = True

    while last:
        result = os.path.join(path, const.CONF_NAME)
        if os.path.exists(result):
            return result
        path, last = os.path.split(path)

    return None


def get(param, default=None):
    """Returns a single configuration parameter or default value."""
    try:
        return _params.get(param, default)
    except TypeError:
        raise NotInitializedException()


def conf_file():
    _check(_path)
    return _path


def site_dir():
    """Returns site source directory."""
    _check(_path)
    return os.path.dirname(_path)


def generic_dir():
    """Returns full path to the generic directory."""
    path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(path, const.GENERIC_DIR)


def commons():
    """Site-wide environmental parameters for page building."""
    return {
        'root_url': get('root_url'),
        'rel_root_url': get('rel_root_url'),
        'site_title': get('title'),
        'site_subtitle': get('subtitle'),
        'menu': get('menu'),
        'time': datetime.now(),
        'author': get('author'),
        'author_url': get('author_url'),
        'generator': const.GENERATOR,
        'generator_url': const.GENERATOR_URL,
        'generator_version': version.get_version(),
        'source_url': get('source_url'),
        'enable_search_form': get('enable_search_form'),
        'atom_url': get('root_url') + get('atom_location'),
        'archive_rel_url': get('rel_root_url') + get('archive_location'),
        'tags_rel_url':
            os.path.dirname(get('rel_root_url') + get('tag_location')) + '/',
        'sitemap_url': get('rel_root_url') + 'sitemap.xml',
        'author_twitter': get('humans_author_twitter'),
        'author_location': get('humans_author_location'),
        'language': get('humans_language'),
        'doctype': get('humans_doctype'),
        'ide': get('humans_ide'),
        'last_updated': datetime.now(),
        'disqus_short_name': get('disqus_short_name'),
        'addthis_id': get('addthis_id'),
        'pluso_enabled': get('pluso_enabled'),
        'google_analytics_tracking_id': get('google_analytics_tracking_id'),
        'datetime_format': get('datetime_format'),
        'date_format': get('date_format'),
    }


def _dumpopt(opt_name):
    """Serializes configuration option with default value."""
    desc = const.DEFAULTS[opt_name]['desc']
    desc = ("# %s\n" % desc) if desc else ''
    return desc + yaml.dump({
        opt_name: const.DEFAULTS[opt_name]['value']
    }, width=79, indent=2, default_flow_style=False)


def _check(value):
    if not value:
        raise NotInitializedException()


def _purify(params):
    """Preprocess configuration parameters."""

    expandables = [
        'pages_path',
        'posts_path',
        'assets_path',
        'build_path',
        'tpl_path',
        'images_path',
        'log_file',
    ]

    for param in expandables:
        params[param] = _expand(params[param])

    urls = [
        'root_url',
        'rel_root_url',
        'source_url',
    ]

    for param in urls:
        params[param] = _trsl(params[param].strip())

    integers = [
        'port',
        'log_max_size',
        'log_backup_cnt',
    ]

    for param in integers:
        params[param] = int(params[param])

    if isinstance(params['time_format'], str):
        params['time_format'] = [params['time_format']]

    menu = params['menu']
    for item in menu:
        item['href'] = item['href'].strip() if 'href' in item else ''
        item['title'] = item['title'].strip() if 'title' in item else ''

    params['verbose'] = params['verbose'] or const.ENV_VERBOSE in os.environ

    return params


def _expand(rel_path):
    """Expands relative path using configuration file location as base
    directory. Absolute pathes will be returned as is."""
    path = rel_path
    if not os.path.isabs(path):
        base = os.path.dirname(os.path.abspath(_path))
        path = os.path.join(base, path)
    return path.rstrip(os.sep + os.altsep)


def _trsl(url):
    """Guarantees the URL have a single trailing slash."""
    return url.rstrip('/') + '/'

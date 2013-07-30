# coding: utf-8

"""Configuration-related fuctionality and defaults"""

import codecs
from datetime import datetime
import os
import yaml
from publicstatic import const
from publicstatic.version import get_version

_params = {}  # Configuration parameters
_conf_file = ''  # Configuration file absolute path


def defaults():
    p_names = map(lambda p: p['name'], const.DEFAULTS)
    p_values = map(lambda p: p['value'], const.DEFAULTS)
    return dict(zip(p_names, p_values))


def load(conf_path):
    """Initializes configuration"""

    global _conf_file
    _conf_file = find_conf(conf_path or '.')

    if not _conf_file:
        raise Exception('configuration file not found')

    try:
        with codecs.open(_conf_file, mode='r', encoding='utf8') as f:
            loaded = yaml.load(f.read())
    except (IOError, OSError) as e:
        raise Exception('error reading configuration file') from e

    global _params
    _params = defaults()
    _params.update(dict((item, loaded[item]) for item in loaded))
    _params = _purify(_params)


def generate(conf_path):  # force=False
    """Generates new configuration file using defaults"""

    global _conf_file
    _conf_file = os.path.join(os.path.abspath(conf_path), const.CONF_NAME)

    if os.path.isdir(site_dir()):  # and not force
        raise Exception("directory already exists: '%s'" % site_dir())
    else:
        os.makedirs(site_dir())

    text = '\n'.join([_dump_option(option) for option in const.DEFAULTS])
    with codecs.open(_conf_file, mode='w', encoding='utf8') as f:
        f.write(text)

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


def get(param):
    """Returns a single configuration parameter"""
    try:
        return _params[param]
    except KeyError:
        raise Exception('Unknown configuration parameter')
    except TypeError:
        raise Exception('Configuration was not initialized')


def conf_file():
    _check(_conf_file)
    return _conf_file


def site_dir():
    _check(_conf_file)
    return os.path.dirname(_conf_file)


def _dump_option(option):
    name, value, desc = option['name'], option['value'], option['desc']
    srl = yaml.dump({name: value}, width=80, indent=4, default_flow_style=False)
    return ''.join([("# %s\n" % desc) if desc else '', srl])


def _check(value):
    if not value:
        raise Exception('configuration was not initialized')


def _purify(params):
    """Preprocess configuration parameters"""
    params['pages_path'] = _expand(params['pages_path'])
    params['posts_path'] = _expand(params['posts_path'])
    params['assets_path'] = _expand(params['assets_path'])
    params['build_path'] = _expand(params['build_path'])
    params['tpl_path'] = _expand(params['tpl_path'])
    params['prototypes_path'] = _expand(params['prototypes_path'])

    params['root_url'] = _trslash(params['root_url'].strip())
    params['rel_root_url'] = _trslash(params['rel_root_url'].strip())
    params['source_url'] = _trslash(params['source_url'].strip())

    params['browser_delay'] = float(params['browser_delay'])
    params['port'] = int(params['port'])

    params['log_file'] = params['log_file'].strip()
    params['log_max_size'] = int(params['log_max_size'])
    params['log_backup_cnt'] = int(params['log_backup_cnt'])

    if isinstance(params['time_format'], str):
        params['time_format'] = [params['time_format']]

    # If there is no {suffix}, include it before extension
    post_loc = params['post_location']
    if '{suffix}' not in post_loc:
        name, ext = os.path.splitext(post_loc)
        params['post_location'] = ''.join([name, '{suffix}', ext])

    menu = params['menu']
    for item in menu:
        item['href'] = item['href'].strip() if 'href' in item else ''
        item['title'] = item['title'].strip() if 'title' in item else ''
    return params


def _expand(rel_path):
    """Expands relative path using configuration file location as base
    directory. Absolute pathes will be returned as is."""
    if not os.path.isabs(rel_path):
        base = os.path.dirname(os.path.abspath(_conf_file))
        rel_path = os.path.join(base, rel_path)
    return rel_path


def  _trslash(url):
    """Guarantees the URL have a single trailing slash"""
    return url.rstrip('/') + '/'

# coding: utf-8

"""Configuration-related fuctionality and defaults"""

import codecs
import os
import yaml

import authoring
import constants

_params = {}  # Configuration parameters
_path = ''  # Configuration file absolute path


def init(conf_path, use_defaults=False):
    """Initializes configuration from Baker arguments"""
    global _path
    _path = os.path.abspath(os.path.join(conf_path or '.', constants.CONF_NAME))

    params = dict(constants.DEFAULTS)

    if not use_defaults:  # Reads configuration file and override defaults
        with codecs.open(_path, mode='r', encoding='utf8') as f:
            loaded = yaml.load(f.read())
        loaded = dict((item, loaded[item]) for item in loaded)
        params.update(loaded)

    global _params
    _params = _purify(params)


def get(param):
    """Returns a single configuration parameter"""
    try:
        return _params[param]
    except KeyError:
        raise Exception('Unknown configuration parameter')
    except TypeError:
        raise Exception('Configuration was not initialized')


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
    text = ''.join([f(x) for x in constants.DEFAULTS])
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
    params['prototypes_path'] = _expand(params['prototypes_path'])
    params['min_js_cmd'] = params['min_js_cmd'].strip()
    params['min_css_cmd'] = params['min_css_cmd'].strip()
    params['sync_cmd'] = params['sync_cmd'].strip()
    params['browser_delay'] = float(params['browser_delay'])
    params['port'] = int(params['port'])
    params['root_url'] = _trslash(params['root_url'].strip())
    params['rel_root_url'] = _trslash(params['rel_root_url'].strip())
    params['log_file'] = params['log_file']
    params['log_max_size'] = int(params['log_max_size'])
    params['log_backup_cnt'] = int(params['log_backup_cnt'])
    menu_items = []
    for item in params['menu']:
        if ':' in item:
            title, url = item.split(':')
        else:
            title = url = item
        menu_items.append({'url': url, 'title': title})
    params['menu'] = menu_items
    return params


def _expand(rel_path):
    """Expands relative path using configuration file location as base
    directory. Absolute pathes will be returned as is."""
    if not os.path.isabs(rel_path):
        base = os.path.dirname(os.path.abspath(_path))
        rel_path = os.path.join(base, rel_path)
    return rel_path


def  _trslash(url):
    """Guarantees the URL have a single trailing slash"""
    return url.rstrip('/') + '/'

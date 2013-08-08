# coding: utf-8

"""Configuration-related fuctionality and defaults."""

import codecs
from datetime import datetime
import os
import re
import yaml
from publicstatic import const
from publicstatic.version import get_version

_params = {}  # Configuration parameters
_path = ''  # Configuration file absolute path


def defaults():
    """Returns default configuration."""
    return {key: value['value'] for key, value in const.DEFAULTS.items()}


def load(conf_path):
    """Initializes configuration."""
    global _path
    _path = find_conf(conf_path or '.')

    if not _path:
        raise Exception('configuration file not found')

    try:
        with codecs.open(_path, mode='r', encoding='utf-8') as f:
            loaded = yaml.load(f.read())
    except (IOError, OSError) as ex:
        raise Exception('error reading configuration file') from ex

    global _params
    _params = defaults()
    _params.update(dict((item, loaded[item]) for item in loaded))
    _params = _purify(_params)


def generate(conf_path):  # force=False
    """Generates new configuration file using defaults."""
    global _path
    _path = os.path.join(os.path.abspath(conf_path), const.CONF_NAME)

    if os.path.isdir(site_dir()):
        raise Exception("directory already exists: '%s'" % site_dir())
    else:
        os.makedirs(site_dir())

    exports = [opt for opt in const.DEFAULTS.keys() if opt in const.EXPORTS]
    text = '\n'.join([_dumpopt(opt) for opt in exports])
    with codecs.open(_path, mode='w', encoding='utf-8') as f:
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
    """Returns a single configuration parameter."""
    try:
        return _params[param]
    except KeyError:
        raise Exception('unknown configuration parameter: "%s"' % param)
    except TypeError:
        raise Exception('configuration was not initialized')


def conf_file():
    _check(_path)
    return _path


def site_dir():
    """Returns site source directory."""
    _check(_path)
    return os.path.dirname(_path)


def gen_dir():
    """Returns generic site directory within the package."""
    path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(path, const.GENERIC_PATH)


def _dumpopt(opt_name):
    """Serializes configuration option with default value."""
    desc = const.DEFAULTS[opt_name]['desc']
    desc = ("# %s\n" % desc) if desc else ''
    return desc + yaml.dump({
            opt_name: const.DEFAULTS[opt_name]['value']
        }, width=79, indent=2, default_flow_style=False)


def _check(value):
    if not value:
        raise Exception('configuration was not initialized')


def _purify(params):
    """Preprocess configuration parameters."""
    params['pages_path'] = _expand(params['pages_path'])
    params['posts_path'] = _expand(params['posts_path'])
    params['assets_path'] = _expand(params['assets_path'])
    params['build_path'] = _expand(params['build_path'])
    params['tpl_path'] = _expand(params['tpl_path'])
    params['prototypes_path'] = _expand(params['prototypes_path'])
    params['root_url'] = _trslash(params['root_url'].strip())
    params['rel_root_url'] = _trslash(params['rel_root_url'].strip())
    params['source_url'] = _trslash(params['source_url'].strip())
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
    path = rel_path
    if not os.path.isabs(path):
        base = os.path.dirname(os.path.abspath(_path))
        path = os.path.join(base, path)
    return path.rstrip(os.sep + os.altsep)


def  _trslash(url):
    """Guarantees the URL have a single trailing slash."""
    return url.rstrip('/') + '/'

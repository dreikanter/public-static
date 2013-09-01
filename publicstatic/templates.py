# coding: utf-8

"""Jinja2 helpers."""

import jinja2
import codecs
from urllib.parse import urlparse
from publicstatic import conf
from publicstatic import helpers
from publicstatic import minify

_env = None

JINJA_EXTENSIONS = [
    'jinja2.ext.loopcontrols',
]


def env():
    global _env
    if _env is None:
        loader = jinja2.FileSystemLoader(searchpath=conf.get('tpl_path'))
        _env = jinja2.Environment(loader=loader, extensions=JINJA_EXTENSIONS)
        _env.filters.update(custom_filters())
    return _env


def custom_filters():
    """Returns a dictionary of custom extensions for Jinja2."""
    return {
        'datetime': filter_datetime,
        'date': filter_date,
        'isodatetime': filter_isodatetime,
        'trimurl': filter_trimurl,
    }


def filter_datetime(value):
    return value.strftime(conf.get('page_datetime_format'))


def filter_date(value):
    if callable(value):
        value = value.__call__()
    return value.strftime(conf.get('page_date_format'))


def filter_isodatetime(value):
    return value.isoformat()


def filter_trimurl(value):
    """Trims addressing scheme (protocol) from the specified url."""
    url = urlparse(value)
    return url.netloc + url.path.rstrip('/')


def template(name=None, path=None):
    """Gets template file contents.

    Arguments:
        name -- template name (file base name w/o extension).
        path -- template file full path, an alternative way to specify
            the template."""
    if name:
        return env().get_template(name)
    elif path:
        with codecs.open(path, mode='r', encoding='utf-8') as f:
            return env().from_string(f.read())
    else:
        raise Exception('either template name or path should be specified')


def render(data, dest, name=None, path=None, utime=None):
    """Render data using a specified template to a file."""
    if not isinstance(data, dict):
        raise Exception('template data should be a dictionary')
    if path is None and name is None:  # use template name from page data
        name = data.get('page', {}).get('template') + '.html'
    result = template(name=name, path=path).render(data)
    if helpers.ext(dest) == '.html' and conf.get('min_html'):
        result = minify.minify_html(result)
    with codecs.open(dest, mode='w', encoding='utf-8') as f:
        f.write(result)
    if utime is not None:
        helpers.utime(dest, utime)

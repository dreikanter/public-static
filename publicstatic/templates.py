# coding: utf-8

"""Jinja2 helpers."""

import jinja2
from urllib.parse import urlparse, urljoin
from publicstatic import conf


_env = None


def filter_datetime(value):
    return value.strftime(conf.get('page_datetime_format'))


def filter_date(value):
    return value.strftime(conf.get('page_date_format'))


def filter_isodatetime(value):
    return value.isoformat()


def filter_trimurl(value):
    """Trims addressing scheme (protocol) from the specified url."""

    url = urlparse(value)
    return url.netloc + url.path.rstrip('/')

def get_template(tpl_name, format='html'):
    """Gets template file contents.

    Arguments:
        tpl_name -- template file name.
        format -- template format (file extension)."""

    global _env

    if _env is None:
        loader = jinja2.FileSystemLoader(searchpath=conf.get('tpl_path'))
        _env = jinja2.Environment(loader=loader)
        _env.filters['datetime'] = filter_datetime
        _env.filters['date'] = filter_date
        _env.filters['isodatetime'] = filter_isodatetime
        _env.filters['trimurl'] = filter_trimurl

    return _env.get_template("%s.%s" % (tpl_name, format))

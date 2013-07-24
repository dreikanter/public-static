# coding: utf-8

"""Jinja2 helpers"""

import jinja2
from . import conf


_env = None


def format_datetime(value):
    return value.strftime(conf.get('page_datetime_format'))


def format_date(value):
    return value.strftime(conf.get('page_date_format'))


def get_template(tpl_name):
    """Gets template file contents.

    Arguments:
        tpl_name -- template name (will be complemented
            to file name using '.mustache')."""

    global _env

    if _env is None:
        loader = jinja2.FileSystemLoader(searchpath=conf.get('tpl_path'))
        _env = jinja2.Environment(loader=loader)
        _env.filters['datetime'] = format_datetime
        _env.filters['date'] = format_date

    return _env.get_template(tpl_name + '.html')

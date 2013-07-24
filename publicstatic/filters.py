# coding: utf-8

"""Jinja2 filters"""

from . import conf


def format_datetime(value):
    return value.strftime(conf.get('page_datetime_format'))


def format_date(value):
    return value.strftime(conf.get('page_date_format'))


def register_filters(env):
    env.filters['datetime'] = format_datetime
    env.filters['date'] = format_date

# coding: utf-8

import csv
import markdown
import re
from publicstatic import templates
from publicstatic import data


EXTENSIONS = [
    'codehilite',
    'def_list',
    'fenced_code',
    'grid',
    'nl2br',
    'smarty',
    data.DataExtension(),
]


def md(text):
    """Converts markdown formatted text to HTML"""
    return markdown.markdown(text.strip(), extensions=EXTENSIONS)

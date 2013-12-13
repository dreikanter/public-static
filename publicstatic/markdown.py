# coding: utf-8

import markdown


EXTENSIONS = [
    'codehilite',
    'def_list',
    'fenced_code',
    'grid',
    'nl2br',
    'smartypants',
]


def md(text):
    """Converts markdown formatted text to HTML"""
    return markdown.markdown(text.strip(), extensions=EXTENSIONS)

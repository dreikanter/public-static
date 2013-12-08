# coding: utf-8

import markdown


EXTENSIONS = [
    'nl2br',
    'grid',
    'smartypants',
    'fenced_code',
    'codehilite',
]


def md(text):
    """Converts markdown formatted text to HTML"""
    return markdown.markdown(text.strip(), extensions=EXTENSIONS)

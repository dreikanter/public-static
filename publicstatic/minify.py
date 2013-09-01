# encoding: utf-8

# This code is forked from django-htmlmin library:
# https://github.com/cobrateam/django-htmlmin

import re
import bs4
from html.parser import HTMLParser

EXCLUDE_TAGS = ('pre', 'script', 'textarea')

COND_RE = re.compile(r"<!--\[if .*\]>.*<!\[endif\]-->")

SPACES_RE = re.compile(r"\s+")


def minify_html(html, ignore_comments=True):
    soup = bs4.BeautifulSoup(html, 'html5lib')
    html = str(soup)
    exclude_tags = {}

    for tag in EXCLUDE_TAGS:
        items = [str(e) for e in soup.findAll(name=tag) if len(e.text) > 0]
        for index, elem in enumerate(items):
            html = html.replace(elem, _tag(tag, index))
        exclude_tags[tag] = items

    soup = bs4.BeautifulSoup(html, 'html5lib')

    if ignore_comments:
        f = lambda text: isinstance(text, bs4.Comment) and not \
                         COND_RE.match(text.output_ready())
        for comment in soup.findAll(text=f):
            comment.extract()

    lines = str(soup).replace(' \n', ' ').split('\n')
    minified_lines = []

    for num, line in enumerate(lines):
        line = line.strip()
        if not _between(line, minified_lines, num):
            line = ' ' + line
        minified_lines.append(line)
        if line.endswith('</a>') and not lines[num + 1].startswith('</body>'):
            minified_lines.append(' ')

    content = SPACES_RE.sub(' ', ''.join(minified_lines))

    for tag in EXCLUDE_TAGS:
        for num, e in enumerate(exclude_tags[tag]):
            content = content.replace(_tag(tag, num), HTMLParser().unescape(e))

    return content


def _between(current_line, all_lines, index):
    return not current_line or \
           current_line.startswith('<') or \
           all_lines[index - 1].endswith('>')


def _tag(tag, index):
    return "<%s>%d</%s>" % (tag, index, tag)

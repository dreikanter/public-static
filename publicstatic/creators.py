# coding: utf-8

"""New pages creation."""

import os
from datetime import datetime
from publicstatic import conf
from publicstatic import helpers
from publicstatic.urlify import urlify


class PageExistsException(Exception):
    pass


def newpage(name, text, force=False):
    """Creates page file.

    Arguments:
        name -- page name (will be used for file name and URL).
        text -- page text.
        force -- True to overwrite existing file; False to throw exception."""
    good_name = urlify(name, ext_map={ord(u'\\'): u'/'})
    file_name = os.path.join(conf.get('pages_path'), good_name) + '.md'
    if os.path.exists(file_name) and not force:
        raise PageExistsException()

    created = datetime.now().strftime(conf.get('time_format')[0])
    text = text.format(title=name, created=created)
    helpers.newfile(file_name, text)
    return file_name


def newpost(name, text='', force=False):
    """Create new post file placeholder with a unique name.

    Arguments:
        name -- post name.
        text -- post text.
        force -- True to overwrite existing file; False to throw exception."""
    created = datetime.now()
    file_name = conf.get('post_source_name').format(
            year=created.strftime('%Y'),
            month=created.strftime('%m'),
            day=created.strftime('%d'),
            name=urlify(name) or const.UNTITLED_POST
        )
    post_path = os.path.join(conf.get('posts_path'), file_name)

    count = 1
    while True:
        file_name = helpers.suffix(post_path, count)
        if force or not os.path.exists(file_name):
            created = created.strftime(conf.get('time_format')[0])
            post_contents = text.format(title=name, created=created)
            helpers.newfile(file_name, post_contents)
            break
        count += 1
    return file_name

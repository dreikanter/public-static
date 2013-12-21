# coding: utf-8

"""General purpose helper functions"""

import codecs
from datetime import datetime
import os
import re
import shutil
import sys
import time
from publicstatic import conf
from publicstatic.urlify import urlify

RE_H1 = re.compile(r"^\s*#\s*(.*)\s*", re.I | re.M | re.U)


def makedirs(dir_path):
    """Creates directory if it not exists."""
    if dir_path and not os.path.isdir(dir_path):
        os.makedirs(dir_path)
        return True
    return False


def browse(url, delay):
    """Opens specified @url with system default browser
    after @delay seconds."""
    time.sleep(delay)
    from webbrowser import open_new_tab
    open_new_tab(url)


def parse_time(value, default=None):
    """Converts string to datetime using the first of the preconfigured
    time_format values that will work."""
    if not value and default:
        return default
    for time_format in conf.get('time_format'):
        try:
            return datetime.strptime(value.strip(), time_format)
        except ValueError:
            pass
    else:
        raise Exception('bad date/time format')


def check_build(path):
    """Check if the web content was built and exit if it isn't."""
    if not os.path.isdir(path):
        sys.exit("web content directory not exists: '%s'" % path)


def drop_build(path, create=False):
    """Drops the build if it exists"""
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    if create and not os.path.isdir(path):
        os.makedirs(path)


def get_h1(text):
    """Extracts the first h1-header from markdown text."""
    matches = RE_H1.search(text)
    return matches.group(1) if matches else ''


def copydir(source, dest, indent=0):
    """Copy a directory structure overwriting existing files."""
    for root, dirs, files in os.walk(source):
        if not os.path.isdir(root):
            os.makedirs(root)
        for each_file in files:
            rel_path = root.replace(source, '').lstrip(os.sep)
            dest_dir = os.path.join(dest, rel_path)
            dest_path = os.path.join(dest_dir, each_file)
            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir)
            shutil.copyfile(os.path.join(root, each_file), dest_path)


def walk(path, operation):
    """Performs operation for each file in the specified path.

    - Operation should take two arguments: the original path and
      additional relative path to each file.
    - Directory names starting with underscore will be ignored."""
    visible = lambda name: not name.startswith('_')
    for curdir, dirnames, curfiles in os.walk(path):
        dirnames[:] = filter(visible, dirnames)
        for nextfile in curfiles:
            fullpath = os.path.join(curdir, nextfile)
            relpath = fullpath[len(path):].strip(os.sep)
            operation(path, relpath)


def tag_url(tag):
    """Returns relative URL to the specified tag page."""
    tag_location = conf.get('tag_location').format(tag=urlify(tag))
    return conf.get('rel_root_url') + tag_location


def tag_path(tag):
    """Returns full path to the specified tag page."""
    file_name = conf.get('tag_location').format(tag=urlify(tag))
    return os.path.join(conf.get('build_path'), file_name)


def execute(command, source, dest=''):
    """Executes a command with {source} and {dest} parameter replacements."""
    os.system(os.path.expandvars(command.format(source=source, dest=dest)))


def mergedicts(*args):
    """Merge a set of dictionaries."""
    result = {}
    for d in args:
        result.update(d)
    return result


def xsplit(sep, text, strip=False, drop_empty=False):
    """Split a string."""
    result = text.split(sep)
    if strip:
        result = [tag.strip() for tag in result]
    if drop_empty:
        result = filter(None, result)
    return result


def suffix(file_name, number):
    """Insert a numeric suffix before the [file_name] extension,
    if the [number] is greater than 0. Effective suffix value will
    be [number] + 1."""
    base, ext = os.path.splitext(file_name)
    suffix = "-%d" % (number + 1) if number > 0 else ''
    return ''.join([base, suffix, ext])


def newfile(file_name, text=''):
    """Create new or overwrite existing file, and write text."""
    makedirs(os.path.dirname(file_name))
    with codecs.open(file_name, mode='w', encoding='utf-8') as f:
        f.write(text)


def utime(path, value):
    """Set access time and modification time for the specified file
    using datetime value."""
    ts = value.timestamp()
    os.utime(path, (ts, ts))


def ext(file_name):
    """Returns a file name extension in lower case (with leading dot)."""
    return os.path.splitext(file_name)[1].lower()


def unindent(text):
    """Remove multiline text indentation."""
    return '\n'.join(map(str.strip, (str(text) or '').split('\n')))

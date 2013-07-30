# coding: utf-8

"""General purpose helper functions"""

import codecs
from datetime import datetime
import errno
import os
import re
import shutil
import sys
import time
import traceback
import markdown
from publicstatic import conf
from publicstatic import const
from publicstatic.urlify import urlify


RE_IMU = re.I | re.M | re.U
H1_PATTERN = re.compile(r"^\s*#\s*(.*)\s*", RE_IMU)
POST_PATTERN = re.compile(r"[\w\\/]+")
PARAM_PATTERN = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", RE_IMU)


def str2int(value, default=None):
    """Safely converts string value to integer. Returns
    default value if the first argument is not numeric.
    Whitespaces are ok."""

    if type(value) is not int:
        value = str(value).strip()
        value = int(value) if value.isdigit() else default
    return value


def makedirs(dir_path):
    """Creates directory if it not exists"""

    if dir_path and not os.path.isdir(dir_path):
        os.makedirs(dir_path)
        return True
    return False


def browse(url, delay):
    """Opens specified @url with system default browser after @delay seconds"""

    time.sleep(delay)
    from webbrowser import open_new_tab
    open_new_tab(url)


def check_build(path):
    """Check if the web content was built and exit if it isn't"""

    if not os.path.isdir(path):
        sys.exit("web content directory not exists: '%s'" % path)


def drop_build(path, create=False):
    """Drops the build if it exists"""

    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    if create and not os.path.isdir(path):
        os.makedirs(path)


def get_h1(text):
    """Extracts the first h1-header from markdown text"""

    matches = H1_PATTERN.search(text)
    return matches.group(1) if matches else ''


def md(text, extensions):
    """Converts markdown formatted text to HTML"""
    try:
        return markdown.markdown(text.strip(), extensions=extensions)
    except Exception as ex:
        raise Exception('markdown processing error') from ex


def update_humans(source_file, dest_file):
    """Updates 'Last update' field in humans.txt file and saves the result
    to specified location.

    Arguments:
        source_file -- original humans.txt file. See http://humanstxt.org
            for the format details.
        dest_file -- location to save updated humans.txt. File name should
            be included."""

    try:
        with codecs.open(source_file, mode='r', encoding='utf8') as f:
            text = f.read()
        repl = r"\1 " + time.strftime("%Y/%m/%d", time.gmtime())
        text = re.sub(r"^(\s*Last\s+update\s*\:).*", repl, text,
                      flags=RE_IMU, count=1)
        with codecs.open(dest_file, mode='w', encoding='utf8') as f:
            f.write(text)
    except Exception as ex:
        message = "humans.txt processing failed ('%s' to '%s')"
        raise Exception(message % (source_file, dest_file)) from ex


def gen_dir(path=None):
    """Returns generic side directory."""

    gen_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(gen_path, const.GENERIC_PATH, path or '')


def spawn_site(path):
    """Clones generic site to specified directory."""

    copydir(gen_dir(), path)


def prototype(name):
    """Returns full path to specified prototype page."""

    try:
        file_name = os.path.join(conf.get('prototypes_path'), str(name) + '.md')
        with codecs.open(file_name, mode='r', encoding='utf8') as f:
            return f.read()
    except Exception as ex:
        raise Exception("error reading prototype post: '%s'" % str(name)) from ex


def copydir(source, dest, indent = 0):
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


def valid_name(value):
    return POST_PATTERN.match(value)


def post_url(page_data, full=False):
    """Generates post URL from page data."""

    url = conf.get('root_url') if full else conf.get('rel_root_url')
    return page_data and (url +
        post_path(page_data['source'], page_data['created']))


_post_path_cache = {}
_post_names = []


# TODO: Drop redundant ctime value after post ctime cached getter implementation
def post_path(source_file, ctime):
    global _post_path_cache
    global _post_names

    if source_file in _post_path_cache:
        return _post_path_cache[source_file]

    postloc = conf.get('post_location')

    year=ctime.strftime('%Y')
    month=ctime.strftime('%m')
    day=ctime.strftime('%d')
    date=ctime.strftime('%Y%m%d')
    name=page_name(source_file, True)

    count = 1
    suffix = ''

    # Uniquify post file name
    while True:
        result = postloc.format(year=year, month=month, day=day,
                                date=date, name=name, suffix=suffix)

        file_name = os.path.basename(result)
        if file_name in _post_names:
            count += 1
            suffix = "-%d" % count
        else:
            _post_names.append(file_name)
            break

    _post_path_cache[source_file] = result
    return result


def page_name(source_file, trim_time=False, untitled='untitled-post'):
    """Extracts name part from source file name.

    Usage:

        >>> page_name("hello.md")
        "hello"

        >>> page_name("20121005-hola.md", True)
        "hola"

        >>> page_name("20121005.md", True)
        "untitled-post"

        >>> page_name("20121005.md", True, untitled="no-name")
        "no-name"
    """

    name = os.path.splitext(os.path.basename(source_file))[0]
    return (name.lstrip('0123456789-_') or untitled) if trim_time else name


def feed_data(page_data):
    """Returns part of the page data dict, relevant to feed generation."""

    return {
        'source': page_data.get('source'),
        'title': page_data.get('title'),
        'created': page_data.get('created'),
        'updated': page_data.get('updated'),
        'author': page_data.get('author', conf.get('author')),
        'url': post_url(page_data),
        'full_url': post_url(page_data, True),
        'content': page_data.get('content'),
        'tags': page_data.get('tags'),
    }


def dest(build_path, rel_source):
    """Gets destination file path."""

    base, ext = os.path.splitext(rel_source)
    new_ext = {
        '.md': '.html',
        '.less': '.css',
    }

    return os.path.join(build_path, base + new_ext.get(ext, ext))


def walk(path, operation):
    """Performs operation for each file in the specified path.
    Operation should take two arguments: the original path and
    additional relative path to each file."""

    for curdir, _, curfiles in os.walk(path):
        for nextfile in curfiles:
            fullpath = os.path.join(curdir, nextfile)
            relpath = fullpath[len(path):].strip(os.sep)
            operation(path, relpath)


def posts(path):
    """Returns a list of post relative pathes in chronological order."""

    posts = []
    walk(path, lambda root, rel:
        posts.append((rel, _page_ctime(os.path.join(root, rel)))))
    posts.sort(key=lambda item: item[1])
    return posts


def _page_ctime(source_file):
    """Gets post/page creation time using header or file system data."""

    result = None
    try:
        with codecs.open(source_file, mode='r', encoding='utf8') as f:
            for line in f.readlines():
                match = PARAM_PATTERN.match(line)
                if not match:
                    break
                if match.group(1).lower() == 'created':
                    result = parse_time(match.group(2))
                    break
    except:
        pass
    return result or datetime.fromtimestamp(os.path.getctime(source_file))


# TODO: Consider file time extraction optimization (use one-time reading)
def parse_time(value):
    """Converts string to datetime using the first of the preconfigured
    time_format values that will work."""

    if value:
        for timef in conf.get('time_format'):
            try:
                return datetime.strptime(value.strip(), timef)
            except:
                pass
    raise Exception('bad date/time format')


def parse_param(text):
    """Parse '<key>: <value>' string to (str, str) tuple. Returns None
    when parsing fails."""

    match = PARAM_PATTERN.match(text)
    if match:
        return (match.group(1).strip().lower(), match.group(2).strip())
    else:
        return None


def tag_url(tag, full=False):
    url = conf.get('root_url') if full else conf.get('rel_root_url')
    return "{url}tags/{tag}.html".format(url=url, tag=urlify(tag))


def execute(command, source, dest=''):
    """Executes a command with {source} and {dest} parameter replacements."""

    os.system(os.path.expandvars(command.format(source=source, dest=dest)))

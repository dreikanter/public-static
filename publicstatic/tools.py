"""General purpose helper functions"""

import codecs
import conf
from datetime import datetime
import errno
import logging
import os
import re
import shutil
import sys
import time
import traceback

import markdown

GENERIC_PATH = 'generic-site'
GENERIC_PAGES = 'generic-pages'
FEED_DIR = 'feed'

RE_FLAGS = re.I | re.M | re.U
H1_PATTERN = re.compile(r"^\s*#\s*(.*)\s*", RE_FLAGS)
POST_PATTERN = re.compile(r"[\w\\/]+")
URI_SEP_PATTERN = re.compile(r"[^a-z\d\%s]+" % os.sep, RE_FLAGS)
URI_EXCLUDE_PATTERN = re.compile(r"[,.`\'\"\!@\#\$\%\^\&\*\(\)\+]+", RE_FLAGS)

log = logging.getLogger()


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
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
        return True
    return False


def execute_proc(command, source, dest=None):
    """Executes one of the preconfigured commands
    with {source} and {dest} parameters replacement"""
    if dest:
        cmd = command.format(source=source, dest=dest)
    else:
        cmd = command.format(source=source)
    execute(os.path.expandvars(cmd))


def execute(cmd, critical=False):
    """Execute system command"""
    try:
        log.debug("executing '%s'" % cmd)
        os.system(cmd)
    except:
        log.error('error executing system command')
        if critical:
            raise
        else:
            log.debug(traceback.format_exc())


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


def purify_time(page, time_parm, default):
    """Returns time value from page dict. If there is no
    specified value, default will be returned."""
    if time_parm in page:
        page[time_parm] = time.strptime(page[time_parm], conf.TIME_FMT)
    else:
        page[time_parm] = datetime.fromtimestamp(default)


def md(text, extensions):
    """Converts markdown formatted text to HTML"""
    try:
        # New Markdown instanse works faster on large amounts of text
        # than reused one (for some reason)
        mkdn = markdown.Markdown(extension=extensions)
    except:
        log.error('markdown initialization error: '
                  'probably bad extension names')
        raise

    try:
        return mkdn.convert(text.strip())
    except:
        log.error('markdown processing error')
        raise


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
                      flags=RE_FLAGS, count=1)
        with codecs.open(dest_file, mode='w', encoding='utf8') as f:
            f.write(text)
    except:
        message = "humans.txt processing failed ('%s' to '%s')"
        log.error(message % (source_file, dest_file))
        raise


def spawn(path):
    """Clones generic site to specified directory"""
    if os.path.isdir(path):
        raise Exception("directory already exists: '%s'" % path)

    generic = os.path.dirname(os.path.abspath(__file__))
    generic = os.path.join(generic, GENERIC_PATH)
    cp(generic, path)


def get_generic(name):
    """Returns full path to specified generic page"""
    try:
        generic = os.path.dirname(os.path.abspath(__file__))
        generic = os.path.join(generic, GENERIC_PAGES)
        generic = os.path.join(generic, str(name) + '.md')
        with codecs.open(generic, mode='r', encoding='utf8') as f:
            return f.read()
    except:
        log.error("error reading generic post: '%s'" % str(name))
        raise


def cp(src, dest):
    """Copies everything to anywhere"""
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            raise


def urlify(string):
    """Make a string URL-safe by excluding unwanted characters
    and replacing spaces with dashes. Used to generate URIs from
    post titles.

    Usage:

        >>> urlify("Hello World")
        "hello-world"

        >>> urlify("Drugs, Sex and Rock'n'Roll!")
        "drugs-sex-and-rocknroll"

        >>> urlify("long/way home")
        "long/way-home"
    """
    result = URI_EXCLUDE_PATTERN.sub('', string)
    if os.altsep:
        result = result.replace(os.altsep, os.sep)
    result = URI_SEP_PATTERN.sub('-', result)
    return result.strip('-').lower()


def feed_name(path, root):
    """Gets feed name from the feed path

    Usage:
        >>> feed_name('/test/pages/feed/', '/test/pages')
        ''

        >>> feed_name('/test/pages/blog/feed', '/test/pages')
        'blog'

        >>> feed_name('/test/pages/other/blog/feed/', '/test/pages')
        'other/blog'
    """
    path = path[len(root):]
    while True:
        path, next = os.path.split(path)
        if next == 'feed' or not path:
            return path.strip(os.sep + os.altsep)


def valid_name(value):
    return POST_PATTERN.match(value)


def get_page_url(page_data):
    got_id = page_data and 'id' in page_data
    return ("/%s.html" % str(page_data['id'])) if got_id else None


def get_page_meta(page_data):
    return {
        'title': page_data['title'],
        'ctime': page_data['ctime'],
        'mtime': page_data['mtime'],
        'author': page_data['author'],
    }


def get_dest(build_path, rel_source):
    """Gets relative destination file path"""
    base, ext = os.path.splitext(rel_source)

    new_ext = {
        '.md': '.html',
        '.less': '.css',
    }

    rel_dest = base + (new_ext[ext] if ext in new_ext else ext)
    return os.path.join(build_path, rel_dest)

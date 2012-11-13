# coding: utf-8

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
PARAM_PATTERN = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", RE_FLAGS)

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


def spawn_site(path):
    """Clones generic site to specified directory"""
    if os.path.isdir(path):
        raise Exception("directory already exists: '%s'" % path)

    generic = os.path.dirname(os.path.abspath(__file__))
    generic = os.path.join(generic, GENERIC_PATH)
    cp(generic, path)


def prototype(name):
    """Returns full path to specified prototype page"""
    try:
        file_name = os.path.join(conf.get('prototypes_path'), str(name) + '.md')
        with codecs.open(file_name, mode='r', encoding='utf8') as f:
            return f.read()
    except:
        log.error("error reading prototype post: '%s'" % str(name))
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


def valid_name(value):
    return POST_PATTERN.match(value)


def post_url(page_data, full=False):
    """Generates post URL from page data"""
    url = conf.get('root_url') if full else conf.get('rel_root_url')
    return page_data and (url +
        post_path(page_data['source'], page_data['created']))


def post_path(source_file, ctime):
    result = conf.get('post_location')
    return result.format(year=ctime.strftime('%Y'),
                         month=ctime.strftime('%m'),
                         day=ctime.strftime('%d'),
                         date=ctime.strftime('%Y%m%d'),
                         name=page_name(source_file, True))


def page_name(source_file, trim_time=False):
    """Extracts name part from source file name.

    Usage:

        >>> page_name("hello.md")
        "hello"

        >>> page_name("20121005-hola.md", True)
        "hola"
    """
    name = os.path.splitext(os.path.basename(source_file))[0]
    return name.lstrip('0123456789-') if trim_time else name


def feed_data(page_data):
    """Returns part of the page data dict, relevant to feed generation"""
    return {
        'source': page_data.get('source'),
        'title': page_data.get('title'),
        'created': expand_time(page_data.get('created')),
        'updated': expand_time(page_data.get('updated')),
        'createddt': page_data.get('created'),
        'updateddt': page_data.get('updated'),
        'author': page_data.get('author', conf.get('author')),
        'url': post_url(page_data),
        'full_url': post_url(page_data, True),
        'content': page_data.get('content'),
    }


def expand_time(value):
    return value and {
        'year': value.strftime('%Y'),
        'month': value.strftime('%m'),
        'day': value.strftime('%d'),
        'hour': value.strftime('%H'),
        'minute': value.strftime('%M'),
    }


def dest(build_path, rel_source):
    """Gets destination file path"""
    base, ext = os.path.splitext(rel_source)

    new_ext = {
        '.md': '.html',
        '.less': '.css',
    }

    rel_dest = base + (new_ext[ext] if ext in new_ext else ext)
    return os.path.join(build_path, rel_dest)


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
    """Returns a list of post relative pathes in chronological order"""
    posts = []
    walk(path, lambda root, rel:
        posts.append((rel, page_ctime(os.path.join(root, rel)))))
    posts.sort(key=lambda item: item[1])
    return posts


def page_ctime(source_file):
    """Gets post/page creation time using header or file system data"""
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
    except Exception as e:
        log.debug('error reading page ctime: ' + str(e))
    return datetime.fromtimestamp(result or os.path.getctime(source_file))


def parse_time(value):
    """Converts string to datetime using TIME_FMT format"""
    return time.mktime(time.strptime(value.strip(), conf.TIME_FMT))


def parse_param(text):
    """Parse '<key>: <value>' string to (str, str) tuple. Returns None
    when parsing fails."""
    match = PARAM_PATTERN.match(text)
    if match:
        return (match.group(1).strip(), match.group(2).strip())
    else:
        return None

#!/usr/bin/env python
# coding: utf-8

import os
import re
import sys
import time
import shutil
import errno
import codecs
import traceback

from argh import ArghParser, arg
from datetime import datetime
from multiprocessing import Process

import authoring
import markdown
import pystache

import conf

__author__ = authoring.AUTHOR
__email__ = authoring.EMAIL
__copyright__ = authoring.COPYRIGHT
__license__ = authoring.LICENSE
__version_info__ = authoring.VERSION_INFO
__version__ = authoring.VERSION
__status__ = authoring.STATUS
__url__ = authoring.URL

GENERIC_PATH = 'generic-site'
GENERIC_PAGES = 'generic-pages'
FEED_DIR = 'feed'

TIME_FMT = "%Y/%m/%d %H:%M:%S"
RE_FLAGS = re.I | re.M | re.U
PARAM_PATTERN = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", RE_FLAGS)
H1_PATTERN = re.compile(r"^\s*#\s*(.*)\s*", RE_FLAGS)
POST_PATTERN = re.compile(r"[\w\\/]+")
URI_SEP_PATTERN = re.compile(r"[^a-z\d\%s]+" % os.sep, RE_FLAGS)
URI_EXCLUDE_PATTERN = re.compile(r"[,.`\'\"\!@\#\$\%\^\&\*\(\)\+]+", RE_FLAGS)

log = None


def setup(args, use_defaults=False):
    """Init configuration and logger"""
    conf.init(args, use_defaults=use_defaults)
    global log
    log = conf.get_logger()


# Website building ============================================================

def process_dir(path):
    log.debug("source path: '%s'" % path)

    files = []
    feeds = {}

    for curdir, _, curfiles in os.walk(path):
        for nextfile in curfiles:
            fullpath = os.path.join(curdir, nextfile)
            relpath = fullpath[len(path):].strip(os.sep)
            parts = relpath.split(os.sep)
            if 'feed' in parts:
                pos = parts.index('feed')
                feed = os.sep.join(parts[:pos])
                if not feed in feeds:
                    feeds[feed] = []
                feeds[feed].append(os.sep.join(parts[pos + 1:]))
            else:
                files.append(relpath)

    for item in feeds:
        process_feed(path, item, feeds[item])

    for item in files:
        process_file(path, item)


def process_feed(path, name, entities):
    pass


def process_file(source_root, source_file):
    """Process single file.

    Arguments:
        source_root -- root files directory (e.g. 'pages').
        source_file -- source file abs path to process."""

    rel_source = source_file  # os.path.relpath(os.path.join(source_root, source_file), source_root)
    source_file = os.path.join(source_root, source_file)
    base, ext = os.path.splitext(rel_source)

    new_ext = {
        '.md': '.html',
        '.less': '.css',
    }

    rel_dest = base + (new_ext[ext] if ext in new_ext else ext)
    dest_file = os.path.join(conf.get('build_path'), rel_dest)
    makedirs(os.path.dirname(dest_file))

    if ext == '.md':
        log.info("building page: %s => %s" % (rel_source, rel_dest))
        build_page(source_file, dest_file, conf.get('templates_path'))

    elif ext == '.less':
        log.info('compiling LESS: ' + rel_source)
        if conf.get('minify_less'):
            tmp_file = dest_file + '.tmp'
            execute_proc('less_cmd', source_file, tmp_file)
            execute_proc('minify_css_cmd', tmp_file, dest_file)
            os.remove(tmp_file)
        else:
            execute_proc('less_cmd', source_file, dest_file)

    elif ext == '.css' and conf.get('minify_css') and conf.get('minify_css_cmd'):
        log.info('minifying CSS: ' + rel_source)
        execute_proc('minify_css_cmd', source_file, dest_file)

    elif ext == '.js' and conf.get('minify_js') and conf.get('minify_js_cmd'):
        log.info('minifying JS: ' + rel_source)
        execute_proc('minify_js_cmd', source_file, dest_file)

    elif os.path.basename(source_file) == 'humans.txt':
        log.info('copying: %s (updated)' % rel_source)
        update_humans(source_file, dest_file)

    else:
        log.info('copying: ' + rel_source)
        shutil.copyfile(source_file, dest_file)


def build_page(source_file, dest_file, templates_path):
    """Builds a page from markdown source amd mustache template"""
    try:
        page = read_page(source_file)
        with codecs.open(dest_file, mode='w', encoding='utf8') as f:
            tpl = get_template(page['template'], templates_path)
            f.write(pystache.render(tpl, page))
    except Exception as e:
        log.debug(traceback.format_exc())
        log.error('content processing error: ' + str(e))


def read_page(source_file):
    """Reads a page file to dictionary.
    Refer readme for page format description."""
    try:
        page = {}
        with codecs.open(source_file, mode='r', encoding='utf8') as f:
            # Extract page metadata if there are some header lines
            lines = f.readlines()
            for num, line in enumerate(lines):
                match = PARAM_PATTERN.match(line)
                if match:
                    page[match.group(1)] = match.group(2).strip()
                else:
                    page['content'] = ''.join(lines[num:])
                    break

        page['title'] = page.get('title', get_h1(page['content'])).strip()
        page['template'] = page.get('template', conf.get('template')).strip()
        page['author'] = page.get('author', conf.get('author')).strip()
        page['content'] = md(page.get('content', ''))

        # Take date/time from file system if not explicitly defined
        purify_time(page, 'ctime', os.path.getctime(source_file))
        purify_time(page, 'mtime', os.path.getmtime(source_file))

        return page

    except:
        log.debug(traceback.format_exc())
        log.error("page processing error '%s'" % source_file)
        return {}


def get_template(tpl_name, templates_path):
    """Gets template file contents.

    Arguments:
        tpl_name -- template name (will be complemented
            to file name using '.mustache').
        templates_path -- template files path."""
    file_name = os.path.join(templates_path, tpl_name + '.mustache')
    if os.path.exists(file_name):
        with codecs.open(file_name, mode='r', encoding='utf8') as f:
            return f.read()

    raise Exception("template not exists: '%s'" % file_name)


# General helpers =============================================================

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
        log.debug("creating directory '%s'" % dir_path)
        os.makedirs(dir_path)


def execute_proc(cmd_name, source, dest=None):
    """Executes one of the preconfigured commands
    with {source} and {dest} parameters replacement"""
    if dest:
        cmd = conf.get(cmd_name).format(source=source, dest=dest)
    else:
        cmd = conf.get(cmd_name).format(source=source)
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
        raise Exception("web content directory not exists: '%s'" % path)


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
        page[time_parm] = time.strptime(page[time_parm], TIME_FMT)
    else:
        page[time_parm] = datetime.fromtimestamp(default)


def md(text):
    """Converts markdown formatted text to HTML"""
    try:
        # New Markdown instanse works faster on large amounts of text
        # than reused one (for some reason)
        mkdn = markdown.Markdown(extensions=conf.get('markdown_extensions'))
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


def create_page(name, date, text, force):
    """Creates page file"""
    name = urlify(name)
    page_path = os.path.join(conf.get('contents_path'), name) + '.md'

    if os.path.exists(page_path):
        if force:
            log.debug('existing page will be overwritten')
        else:
            raise Exception('page already exists, use -f to overwrite')

    text = text.format(title=name, ctime=date.strftime(TIME_FMT))
    makedirs(os.path.split(page_path)[0])

    with codecs.open(page_path, mode='w', encoding='utf8') as f:
        log.debug("creating page '%s'" % page_path)
        f.write(text)


def create_post(name, date, text, force):
    """Generates post file placeholder with an unique name
    and returns its name"""

    feed, post = os.path.split(name)

    try:
        parts = [conf.get('contents_path'), feed, FEED_DIR, date.strftime('%Y')]
        path = os.sep.join(parts)
        makedirs(path)
    except:
        log.error("error creating new feed at '%s'" % path)
        raise

    # Generate new post file name
    parts = [date.strftime('%Y-%m-%d'), urlify(post)]
    post = '_'.join(filter(None, parts))
    num = 1

    # Preserve file with a new unique name
    while True:
        sfx = str(num) if num > 1 else ''
        result = os.path.join(path, post) + sfx + '.md'

        if force or not os.path.exists(result):
            log.debug("creating post '%s'" % result)
            text = text.format(title=name, ctime=date.strftime(TIME_FMT))
            with codecs.open(result, mode='w', encoding='utf8') as f:
                f.write(text)
            break

        num += 1

    return result


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


# Commands

source_arg = arg('-s', '--source', default=None, metavar='SRC',
                 help='website source path (default is the current directory)')

log_arg = arg('-l', '--log', default=None,
              help='log file name')

verbose_arg = arg('-v', '--verbose', default=False,
                  help='verbose output')

force_arg = arg('-f', '--force', default=False,
                help='overwrite existing files')

type_arg = arg('-t', '--type', default=None,
               help='generic page to clone')

edit_arg = arg('-e', '--edit', default=False,
               help='open with preconfigured editor')


@source_arg
@log_arg
@verbose_arg
def init(args):
    """create new website"""
    setup(args, use_defaults=True)

    try:
        spawn(os.path.dirname(conf.get_path()))
        conf.write_defaults()
        log.info('website created successfully, have fun!')
    except:
        log.error('initialization failed')
        raise


@source_arg
@log_arg
@verbose_arg
def build(args):
    """generate web content from source"""
    setup(args)
    drop_build(conf.get('build_path'))
    makedirs(conf.get('build_path'))
    log.info("building path: '%s'" % conf.get('build_path'))
    log.info('processing assets...')
    process_dir(conf.get('assets_path'))
    log.info('processing contents...')
    process_dir(conf.get('contents_path'))
    log.info('done')

    # TODO: Build feeds
    # rebuild index - text file: path->title
    # update archive page
    # update rss
    # update atom


@source_arg
@arg('-p', '--port', default=None, help='port for local HTTP server')
@arg('-b', '--browse', default=False, help='open in default browser')
@log_arg
@verbose_arg
def run(args):
    """run local web server to preview generated website"""
    setup(args)
    check_build(conf.get('build_path'))
    original_cwd = os.getcwd()
    port = str2int(args.port, conf.get('port'))
    log.info("running HTTP server on port %d..." % port)

    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from SocketServer import TCPServer
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(('', port), handler)

    try:
        if args.browse:
            url = "http://localhost:%s/" % port
            delay = conf.get('browser_opening_delay')
            log.info("opening browser in %g seconds" % delay)
            p = Process(target=browse, args=(url, delay))
            p.start()

        log.info('use Ctrl-Break to stop webserver')
        os.chdir(conf.get('build_path'))
        httpd.serve_forever()

    except KeyboardInterrupt:
        log.info('server was stopped by user')
    finally:
        os.chdir(original_cwd)


@source_arg
@log_arg
@verbose_arg
def deploy(args):
    """deploy generated website to the remote web server"""
    setup(args)
    check_build(conf.get('build_path'))

    if not conf.get('sync_cmd'):
        raise Exception('synchronizing command is not '
                        'defined by configuration')

    log.info('synchronizing...')
    execute(conf.get('sync_cmd').format(path=conf.get('build_path')), True)
    log.info('done')


@source_arg
@log_arg
@verbose_arg
def clean(args):
    """delete all generated content"""
    setup(args)
    log.info('cleaning output...')
    drop_build(conf.get('build_path'))
    log.info('done')


@arg('name', help='page name (may include path)')
@source_arg
@force_arg
@edit_arg
@type_arg
@log_arg
@verbose_arg
def page(args):
    """create new page"""
    setup(args)
    if not POST_PATTERN.match(args.name):
        raise Exception('illegal page name')

    text = get_generic(args.type or 'default-page')
    page_path = create_page(args.name, datetime.now(), text, args.force)
    log.info('page cerated')

    if args.edit:
        execute_proc('editor_cmd', page_path)


@arg('name', help='post name and optional feed name')
@source_arg
@force_arg
@edit_arg
@type_arg
@log_arg
@verbose_arg
def post(args):
    """create new post"""
    setup(args)
    if not POST_PATTERN.match(args.name):
        raise Exception('illegal feed or post name')

    text = get_generic(args.type or 'default-post')
    post_path = create_post(args.name, datetime.now(), text, args.force)
    log.info('post cerated')

    if args.edit:
        execute_proc('editor_cmd', post_path)


def main():
    try:
        p = ArghParser()
        p.add_commands([init, build, run, deploy, clean, page, post])
        p.dispatch()
        return 0

    except KeyboardInterrupt:
        log.info('killed by user')
        return 0

    except Exception as e:
        global log
        if not log:  # logging about logging error
            import logging
            logging.basicConfig()
            log = logging

        log.error('loggign initialization error')
        log.error(str(e))
        log.debug(traceback.format_exc())
        return 2


if __name__ == '__main__':
    sys.exit(main())

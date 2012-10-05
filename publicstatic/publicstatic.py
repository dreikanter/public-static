#!/usr/bin/env python
# coding: utf-8

import os
import re
import sys
import shutil
import codecs
import traceback

from argh import ArghParser, arg
from datetime import datetime
from multiprocessing import Process
from pprint import pprint

import pyatom
import pystache

import authoring
import conf
import tools

__author__ = authoring.AUTHOR
__email__ = authoring.EMAIL
__copyright__ = authoring.COPYRIGHT
__license__ = authoring.LICENSE
__version_info__ = authoring.VERSION_INFO
__version__ = authoring.VERSION
__status__ = authoring.STATUS
__url__ = authoring.URL

# TIME_FMT = "%Y/%m/%d %H:%M:%S"
RE_FLAGS = re.I | re.M | re.U
PARAM_PATTERN = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", RE_FLAGS)
# H1_PATTERN = re.compile(r"^\s*#\s*(.*)\s*", RE_FLAGS)
# POST_PATTERN = re.compile(r"[\w\\/]+")
# URI_SEP_PATTERN = re.compile(r"[^a-z\d\%s]+" % os.sep, RE_FLAGS)
# URI_EXCLUDE_PATTERN = re.compile(r"[,.`\'\"\!@\#\$\%\^\&\*\(\)\+]+", RE_FLAGS)

log = None


def setup(args, use_defaults=False):
    """Init configuration and logger"""
    conf.init(args, use_defaults=use_defaults)
    global log
    log = conf.get_logger()


# Website building ============================================================

def process_dir(path):
    """Process a directory containing independent
    files like website pages or assets."""
    log.debug("source path: '%s'" % path)
    for curdir, _, curfiles in os.walk(path):
        for nextfile in curfiles:
            fullpath = os.path.join(curdir, nextfile)
            relpath = fullpath[len(path):].strip(os.sep)
            process_file(path, relpath)


def process_file(root_dir, rel_source):
    """Process single web page source file or static asset.

    Arguments:
        root_dir -- root files directory (e.g. 'pages').
        rel_source -- source file relative path."""

    source_file = os.path.join(root_dir, rel_source)
    ext = os.path.splitext(rel_source)[1]
    dest_file = tools.get_dest(conf.get('build_path'), rel_source)
    tools.makedirs(os.path.dirname(dest_file))

    if ext == '.md':
        log.info('building page:' + rel_source)
        build_page(read_page(source_file), dest_file)

    elif ext == '.less':
        log.info('compiling LESS: ' + rel_source)
        if conf.get('minify_less'):
            tmp_file = dest_file + '.tmp'
            tools.execute_proc(conf.get('less_cmd'), source_file, tmp_file)
            tools.execute_proc(conf.get('minify_css_cmd'), tmp_file, dest_file)
            os.remove(tmp_file)
        else:
            tools.execute_proc(conf.get('less_cmd'), source_file, dest_file)

    elif ext == '.css' and conf.get('minify_css') and conf.get('minify_css_cmd'):
        log.info('minifying CSS: ' + rel_source)
        tools.execute_proc(conf.get('minify_css_cmd'), source_file, dest_file)

    elif ext == '.js' and conf.get('minify_js') and conf.get('minify_js_cmd'):
        log.info('minifying JS: ' + rel_source)
        tools.execute_proc(conf.get('minify_js_cmd'), source_file, dest_file)

    elif os.path.basename(source_file) == 'humans.txt':
        log.info('copying: %s (updated)' % rel_source)
        tools.update_humans(source_file, dest_file)

    else:
        log.info('copying: ' + rel_source)
        shutil.copyfile(source_file, dest_file)


def process_blog(path, name, entities):
    prev = None
    next = None
    index = []

    entnum = len(entities)
    fullpath = lambda i: os.path.join(path, name, 'feed', entities[i])
    dest_dir = os.path.join(conf.get('build_path'), name)
    tools.makedirs(dest_dir)

    for i in range(entnum):
        data = next if next else read_page(fullpath(i), True)
        next = read_page(fullpath(i + 1), True) if (i + 1 < entnum) else None

        index.append(tools.get_page_meta(data))

        data['prev_url'] = tools.get_page_url(prev)
        data['prev_title'] = prev['title'] if prev else None
        data['next_url'] = tools.get_page_url(next)
        data['next_title'] = next['title'] if next else None

        page_file = data['id'] + '.html'
        log.info(" * %s => %s" % (entities[i], os.path.join(name, page_file)))
        dest_file = os.path.join(dest_dir, page_file)
        build_page(data, dest_file, conf.get('templates_path'))

        prev = data

    build_indexes(index, dest_dir)
    build_feeds(index, dest_dir)


def build_page(data, dest_file):
    """Builds a web page

    Arguments:
        data -- page data dict.
        dest_file -- full path to the destination file."""

    try:
        tpl = get_template(data['template'])
        with codecs.open(dest_file, mode='w', encoding='utf8') as f:
            f.write(pystache.render(tpl, data))
    except Exception as e:
        log.debug(traceback.format_exc())
        log.error('content processing error: ' + str(e))


def build_feeds(data, dest_dir):
    """Builds RSS feed"""
    feed = pyatom.AtomFeed(title="",
                           subtitle="",
                           feed_url="",
                           url="",
                           author="")

    for item in data:
        feed.add(title="My Post",
                 content="Body of my post",
                 content_type="html",
                 author="Me",
                 url="http://example.org/entry1",
                 updated=datetime.datetime.utcnow())

    print feed.to_string()


def build_indexes(data, dest_dir):
    """Build post list pages"""
    data = {
        'template': 'archive',
        'title': 'Blog archive',
        'posts': data,
    }

    build_page(data, os.path.join(dest_dir, 'archive.html'))


def read_page(source_file, is_post=False):
    """Reads a post/page file to dictionary"""
    data = {}
    with codecs.open(source_file, mode='r', encoding='utf8') as f:
        # Extract page metadata if there are some header lines
        lines = f.readlines()
        for num, line in enumerate(lines):
            match = PARAM_PATTERN.match(line)
            if match:
                data[match.group(1)] = match.group(2).strip()
            else:
                data['content'] = ''.join(lines[num:])
                break

    data['title'] = data.get('title', tools.get_h1(data['content'])).strip()

    deftpl = conf.get('post_template' if is_post else 'page_template')
    data['template'] = data.get('template', deftpl).strip()
    data['author'] = data.get('author', conf.get('author')).strip()

    extensions = conf.get('markdown_extensions')
    data['content'] = tools.md(data.get('content', ''), extensions)

    data['id'] = get_id(source_file)

    # Take date/time from file system if not explicitly defined
    tools.purify_time(data, 'ctime', os.path.getctime(source_file))
    tools.purify_time(data, 'mtime', os.path.getmtime(source_file))

    return data


def get_id(file_name):
    """Extracts page id from source file path"""
    name = os.path.splitext(os.path.basename(file_name))[0]
    parts = name.split('_', 1)
    return parts[1] if len(parts) > 1 else None


def get_template(tpl_name):
    """Gets template file contents.

    Arguments:
        tpl_name -- template name (will be complemented
            to file name using '.mustache')."""
    file_name = os.path.join(conf.get('templates_path'), tpl_name + '.mustache')
    if os.path.exists(file_name):
        with codecs.open(file_name, mode='r', encoding='utf8') as f:
            return f.read()

    raise Exception("template not exists: '%s'" % file_name)


def create_page(name, text, date, force):
    """Creates page file

    Arguments:
        name -- page name (will be used for file name and URL).
        text -- page text.
        date -- creation date and time (struct_time).
        force -- True to overwrite existing file; False to throw exception."""

    name = tools.urlify(name)
    log.debug("creating page '%s'" % name)
    page_path = os.path.join(conf.get('pages_path'), name) + '.md'

    if os.path.exists(page_path):
        if force:
            log.debug('existing page will be overwritten')
        else:
            log.error('page already exists, use -f to overwrite')
            return None

    text = text.format(title=name, ctime=date.strftime(conf.TIME_FMT))
    tools.makedirs(os.path.split(page_path)[0])

    with codecs.open(page_path, mode='w', encoding='utf8') as f:
        f.write(text)
    return page_path


def create_post(name, text, date, force):
    """Generates post file placeholder with an unique name
    and returns its name

    Arguments:
        name -- post name (will be used for file name and URL).
        text -- post text.
        date -- creation date and time (struct_time).
        force -- True to overwrite existing file; False to throw exception."""

    try:
        post_name = conf.get('post_name').format(year=date.strftime('%Y'),
                                                 month=date.strftime('%m'),
                                                 day=date.strftime('%d'),
                                                 name='{name}')
        # print((conf.get('posts_path'), post_name, os.path.join(conf.get('posts_path'), post_name)))
        # return
        post_path = os.path.join(conf.get('posts_path'), post_name)
        print(os.path.dirname(post_path))
        tools.makedirs(os.path.dirname(post_path))
    except:
        log.error('error creating new post')
        raise

    # Generate new post file name and preserve file with a new unique name
    file_name = tools.urlify(name)
    num = 1
    while True:
        suffix = str(num) if num > 1 else ''
        result = post_path.format(name=file_name + suffix)
        print("writing to '%s'" % result)
        return
        if force or not os.path.exists(result):
            log.debug("creating post '%s'" % result)
            text = text.format(title=name,
                               ctime=date.strftime(conf.TIME_FMT))
            with codecs.open(result, mode='w', encoding='utf8') as f:
                f.write(text)
            return result
        else:
            num += 1


# Common command line arguments

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


# Commands

@source_arg
@log_arg
@verbose_arg
def init(args):
    """create new website"""
    setup(args, use_defaults=True)

    try:
        tools.spawn(os.path.dirname(conf.get_path()))
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
    tools.drop_build(conf.get('build_path'))
    tools.makedirs(conf.get('build_path'))
    log.info("building path: '%s'" % conf.get('build_path'))
    log.info('processing assets...')
    process_dir(conf.get('assets_path'))
    log.info('processing contents...')
    process_dir(conf.get('pages_path'))
    log.info('done')


@source_arg
@arg('-p', '--port', default=None, help='port for local HTTP server')
@arg('-b', '--browse', default=False, help='open in default browser')
@log_arg
@verbose_arg
def run(args):
    """run local web server to preview generated website"""
    setup(args)
    tools.check_build(conf.get('build_path'))
    original_cwd = os.getcwd()
    port = tools.str2int(args.port, conf.get('port'))
    log.info("running HTTP server on port %d..." % port)

    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from SocketServer import TCPServer
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(('', port), handler)

    try:
        if args.browse:
            url = "http://localhost:%s/" % port
            delay = conf.get('browser_open_delay')
            log.info("opening browser in %g seconds" % delay)
            p = Process(target=tools.browse, args=(url, delay))
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
    tools.check_build(conf.get('build_path'))

    if not conf.get('sync_cmd'):
        raise Exception('synchronizing command is not '
                        'defined by configuration')

    log.info('synchronizing...')
    cmd = conf.get('sync_cmd').format(path=conf.get('build_path'))
    tools.execute(cmd, True)
    log.info('done')


@source_arg
@log_arg
@verbose_arg
def clean(args):
    """delete all generated content"""
    setup(args)
    log.info('cleaning output...')
    tools.drop_build(conf.get('build_path'))
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
    if not tools.valid_name(args.name):
        raise Exception('illegal page name')

    text = tools.get_generic(args.type or 'default-page')
    page_path = create_page(args.name, text, datetime.now(), args.force)

    if not page_path:
        return

    log.info('page cerated')
    if args.edit:
        tools.execute_proc(conf.get('editor_cmd'), page_path)


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
    if not tools.valid_name(args.name):
        raise Exception('illegal feed or post name')

    text = tools.get_generic(args.type or 'default-post')
    post_path = create_post(args.name, text, datetime.now(), args.force)
    log.info('post cerated')

    if args.edit:
        tools.execute_proc(conf.get('editor_cmd'), post_path)


def main():
    try:
        p = ArghParser()
        p.add_commands([init, build, run, deploy, clean, page, post])
        p.dispatch()
        return 0

    except KeyboardInterrupt:
        log.info('killed by user')
        return 0

    except SystemExit as e:
        log.info(str(e))

    except Exception as e:
        import logging
        logging.basicConfig()
        logging.error('loggign initialization error')
        logging.error(str(e))
        logging.debug(traceback.format_exc())
        return 2


if __name__ == '__main__':
    sys.exit(main())

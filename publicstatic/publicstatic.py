#!/usr/bin/env python
# coding: utf-8

import os
import re
import sys
import shutil
import codecs
import time
import traceback

from argh import ArghParser, arg
from datetime import datetime
from multiprocessing import Process

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

RE_FLAGS = re.I | re.M | re.U

log = None


def setup(args, use_defaults=False):
    """Init configuration and logger"""
    conf.init(args, use_defaults=use_defaults)
    global log
    log = conf.get_logger()


# Website building

def process_dir(path):
    """Process a directory containing independent
    files like website pages or assets."""
    log.debug("source path: '%s'" % path)
    tools.walk(path, process_file)


def process_file(root_dir, rel_source):
    """Process single web page source file or static asset.

    Arguments:
        root_dir -- root files directory (e.g. 'pages').
        rel_source -- source file relative path."""

    source_file = os.path.join(root_dir, rel_source)
    ext = os.path.splitext(rel_source)[1]
    dest_file = tools.dest(conf.get('build_path'), rel_source)
    tools.makedirs(os.path.dirname(dest_file))

    if ext == '.md':
        log.info("- %s => %s" % (rel_source, os.path.relpath(dest_file, conf.get('build_path'))))
        build_page(parse(source_file), dest_file)

    elif ext == '.less':
        log.info('compiling LESS: ' + rel_source)
        if conf.get('min_less'):
            tmp_file = dest_file + '.tmp'
            tools.execute_proc(conf.get('less_cmd'), source_file, tmp_file)
            tools.execute_proc(conf.get('min_css_cmd'), tmp_file, dest_file)
            os.remove(tmp_file)
        else:
            tools.execute_proc(conf.get('less_cmd'), source_file, dest_file)

    elif ext == '.css' and conf.get('min_css') and conf.get('min_css_cmd'):
        log.info('minifying CSS: ' + rel_source)
        tools.execute_proc(conf.get('min_css_cmd'), source_file, dest_file)

    elif ext == '.js' and conf.get('min_js') and conf.get('min_js_cmd'):
        log.info('minifying JS: ' + rel_source)
        tools.execute_proc(conf.get('min_js_cmd'), source_file, dest_file)

    elif os.path.basename(source_file) == 'humans.txt':
        log.info('copying: %s (updated)' % rel_source)
        tools.update_humans(source_file, dest_file)

    else:
        log.info('copying: ' + rel_source)
        shutil.copyfile(source_file, dest_file)


def process_blog(path):
    posts = tools.posts(path)
    prev = None
    next = None
    index = []

    for i in range(len(posts)):
        source_file, ctime = posts[i]
        data = next if next else parse(os.path.join(path, source_file), is_post=True)
        if i + 1 < len(posts):
            next = parse(os.path.join(path, posts[i + 1][0]), is_post=True)
        else:
            next = None

        dest_file = tools.post_path(source_file, ctime)
        log.info("- %s => %s" % (posts[i][0], dest_file))
        dest_file = os.path.join(conf.get('build_path'), dest_file)
        tools.makedirs(os.path.dirname(dest_file))

        data['prev_url'] = tools.post_url(prev)
        data['prev_title'] = prev['title'] if prev else None
        data['next_url'] = tools.post_url(next)
        data['next_title'] = next['title'] if next else None
        index.append(tools.page_meta(data))
        build_page(data, dest_file)
        prev = data

    # build_indexes(index, dest_dir)
    # build_feeds(index, dest_dir)


def build_page(data, dest_file):
    """Builds a web page

    Arguments:
        data -- page data dict.
        dest_file -- full path to the destination file."""

    try:
        tpl = get_tpl(data['template'])
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


def parse(source_file, is_post=False):
    """Reads a post/page file to dictionary.

    Arguments:
        source_files -- path to the source file.
        is_post -- source file is a blog post.
        header -- returns {file_name, ctime, and title} only."""

    data = {}
    with codecs.open(source_file, mode='r', encoding='utf8') as f:
        # Extract page metadata if header lines presents
        lines = f.readlines()
        for num, line in enumerate(lines):
            parsed = tools.parse_param(line)
            if parsed:
                data[parsed[0]] = parsed[1]
            else:
                data['content'] = ''.join(lines[num:])
                break

    data['source'] = source_file
    data['title'] = data.get('title', tools.get_h1(data['content']))

    deftpl = conf.get('post_tpl' if is_post else 'page_tpl')
    data['template'] = data.get('template', deftpl).strip()
    data['author'] = data.get('author', conf.get('author')).strip()

    extensions = conf.get('markdown_extensions')
    data['content'] = tools.md(data.get('content', ''), extensions)

    data['id'] = get_id(source_file)

    def purify_time(param, get_time):
        if param in data:
            data[param] = tools.parse_time(data[param])
        else:
            data[param] = get_time(source_file)
        data[param] = datetime.fromtimestamp(data[param])

    purify_time('ctime', os.path.getctime)
    purify_time('mtime', os.path.getmtime)

    return data


def get_id(file_name):
    """Extracts page id from source file path"""
    name = os.path.splitext(os.path.basename(file_name))[0]
    parts = name.split('_', 1)
    return parts[1] if len(parts) > 1 else None


def get_tpl(tpl_name):
    """Gets template file contents.

    Arguments:
        tpl_name -- template name (will be complemented
            to file name using '.mustache')."""
    file_name = os.path.join(conf.get('tpl_path'), tpl_name + '.mustache')
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

    post_name = '%s-%s{suffix}.md' % (date.strftime('%Y%m%d'), tools.urlify(name))
    post_path = os.path.join(conf.get('posts_path'), post_name)
    tools.makedirs(os.path.dirname(post_path))

    # Generate new post file name and preserve file with a new unique name
    num = 1
    while True:
        result = post_path.format(suffix=str(num) if num > 1 else '')
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
        tools.spawn_site(os.path.dirname(conf.get_path()))
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
    log.info('processing pages...')
    process_dir(conf.get('pages_path'))
    log.info('processing blog posts...')
    process_blog(conf.get('posts_path'))
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
            delay = conf.get('browser_delay')
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

    text = tools.generic(args.type or 'default-page')
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

    text = tools.generic(args.type or 'default-post')
    try:
        post_path = create_post(args.name, text, datetime.now(), args.force)
    except:
        log.error('error creating new post')
        raise

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

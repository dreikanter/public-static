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

import authoring
import pystache

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
    tools.makedirs(os.path.dirname(dest_file))

    if ext == '.md':
        log.info("building page: %s => %s" % (rel_source, rel_dest))
        build_page(source_file, dest_file, conf.get('templates_path'))

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

        page['title'] = page.get('title', tools.get_h1(page['content'])).strip()
        page['template'] = page.get('template', conf.get('template')).strip()
        page['author'] = page.get('author', conf.get('author')).strip()

        extensions = conf.get('markdown_extensions')
        page['content'] = tools.md(page.get('content', ''), extensions)

        # Take date/time from file system if not explicitly defined
        tools.purify_time(page, 'ctime', os.path.getctime(source_file))
        tools.purify_time(page, 'mtime', os.path.getmtime(source_file))

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
            delay = conf.get('browser_opening_delay')
            log.info("opening browser in %g seconds" % delay)
            p = Process(target=args.browse, args=(url, delay))
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
    tools.execute(conf.get('sync_cmd').format(path=conf.get('build_path')), True)
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
    page_path = tools.create_page(args.name, datetime.now(), text, args.force)
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
    post_path = tools.create_post(args.name, datetime.now(), text, args.force)
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

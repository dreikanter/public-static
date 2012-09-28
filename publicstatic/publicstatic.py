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

    for f in feeds:
        process_feed(path, f, feeds[f])

    for f in files:
        process_file(path, f)


def process_feed(path, name, entities):
    prev = None
    next = None
    index = []

    entnum = len(entities)
    fullpath = lambda i: os.path.join(path, name, 'feed', entities[i])
    dest_path = os.path.join(conf.get('build_path'), name)
    tools.makedirs(dest_path)

    for i in range(entnum):
        data = next if next else read_page(fullpath(i), True)
        next = read_page(fullpath(i + 1), True) if (i + 1 < entnum) else None

        if not index:
            index.append(data)
        else:
            index.append({
                'title': data['title'],
                'ctime': data['ctime'],
                'mtime': data['mtime'],
                'author': data['author'],
            })

        data['prev_url'] = id2url(prev['id']) if prev else None
        data['prev_title'] = id2url(prev['title']) if prev else None
        data['next_url'] = id2url(next['id']) if next else None
        data['next_title'] = id2url(next['title']) if next else None

        page_file = data['id'] + '.html'
        log.info(" * %s => %s" % (entities[i], os.path.join(name, page_file)))
        dest_file = os.path.join(dest_path, page_file)
        build_page(data, dest_file, conf.get('templates_path'))

        prev = data

    build_index(index, os.path.join(dest_path, 'index.html'))


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
        data = read_page(source_file)
        build_page(data, dest_file, conf.get('templates_path'))

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


def build_page(data, dest_file, templates_path):
    """Builds a web page from dict and mustache template"""
    try:
        with codecs.open(dest_file, mode='w', encoding='utf8') as f:
            tpl = get_template(data['template'], templates_path)
            f.write(pystache.render(tpl, data))
    except Exception as e:
        log.debug(traceback.format_exc())
        log.error('content processing error: ' + str(e))


def build_index(data, dest_file):
    # TODO: ...
    pass


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


def id2url(id):
    """Converts page id to relative URL"""
    # TODO: ...
    return "/%s.html" % str(id)


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

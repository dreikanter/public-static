# coding: utf-8

"""public-static - static website builder"""

from datetime import datetime
from multiprocessing import Process
import os
import re
import shutil
import sys
import traceback
from argh import ArghParser, arg
from publicstatic import conf
from publicstatic import builders
from publicstatic import logger
from publicstatic import helpers
from publicstatic.lib.pyatom import AtomFeed
from publicstatic.urlify import urlify
from publicstatic.version import get_version
from publicstatic.templates import get_template


# Common command line arguments

source_arg = arg('-s', '--source', default=None, metavar='SRC',
                 help='website source path (default is the current directory)')

force_arg = arg('-f', '--force', default=False,
                help='overwrite existing file')

type_arg = arg('-t', '--type', default=None,
               help='generic page to clone')

edit_arg = arg('-e', '--edit', default=False,
               help='open with preconfigured editor')


# Commands

@source_arg
def init(args):
    """create new website"""

    conf.generate(args.source)
    try:
        helpers.spawn_site(conf.site_dir())
        logger.info('website created successfully, have fun!')
    except Exception as e:
        logger.error('initialization failed: ' + str(e))
        print(str(e))


@source_arg
def build(args):
    """generate web content from source"""

    conf.load(args.source)
    helpers.drop_build(conf.get('build_path'))
    helpers.makedirs(conf.get('build_path'))

    logger.info("building path: '%s'" % conf.get('build_path'))
    logger.info('processing assets...')
    builders.process_dir(conf.get('assets_path'))

    logger.info('processing blog posts...')
    builders.process_blog(conf.get('posts_path'))

    logger.info('processing pages...')
    builders.process_dir(conf.get('pages_path'))
    logger.info('done')


@source_arg
@arg('-p', '--port', default=None, help='port for local HTTP server')
@arg('-b', '--browse', default=False, help='open in default browser')
def run(args):
    """run local web server to preview generated website"""

    conf.load(args.source)
    helpers.check_build(conf.get('build_path'))
    original_cwd = os.getcwd()
    port = helpers.str2int(args.port, conf.get('port'))
    logger.info("running HTTP server on port %d..." % port)

    from http.server import SimpleHTTPRequestHandler
    from socketserver import TCPServer
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(('', port), handler)

    try:
        if args.browse:
            url = "http://localhost:%s/" % port
            delay = conf.get('browser_delay')
            logger.info("opening browser in %g seconds" % delay)
            p = Process(target=helpers.browse, args=(url, delay))
            p.start()

        logger.info('use Ctrl-Break to stop webserver')
        os.chdir(conf.get('build_path'))
        httpd.serve_forever()

    except KeyboardInterrupt:
        logger.info('server was stopped by user')
    finally:
        os.chdir(original_cwd)


@source_arg
def deploy(args):
    """deploy generated website to the remote web server"""

    conf.load(args.source)
    helpers.check_build(conf.get('build_path'))

    if not conf.get('deploy_cmd'):
        raise Exception('deploy command is not defined')

    logger.info('deploying website...')
    cmd = conf.get('deploy_cmd').format(build_path=conf.get('build_path'))

    from subprocess import call
    call(cmd)

    logger.info('done')


@source_arg
def clean(args):
    """delete all generated content"""

    conf.load(args.source)
    logger.info('cleaning output...')
    helpers.drop_build(conf.get('build_path'))
    logger.info('done')


@arg('name', help='page name (may include path)')
@source_arg
@force_arg
@edit_arg
@type_arg
def page(args):
    """create new page"""

    conf.load(args.source)
    if not helpers.valid_name(args.name):
        raise Exception('illegal page name')

    text = helpers.prototype(args.type or 'default-page')
    page_path = builders.create_page(args.name, text, datetime.now(), args.force)

    if not page_path:
        return

    logger.info('page cerated')
    if args.edit:
        helpers.execute(conf.get('editor_cmd'), page_path)


@arg('name', help='post name and optional feed name')
@source_arg
@force_arg
@edit_arg
@type_arg
def post(args):
    """create new post"""

    conf.load(args.source)
    if not helpers.valid_name(args.name):
        raise Exception('illegal feed or post name')

    text = helpers.prototype(args.type or 'default-post')
    try:
        post_path = builders.create_post(args.name, text, datetime.now(), args.force)
    except:
        logger.error('error creating new post')
        raise

    logger.info('post cerated')

    if args.edit:
        helpers.execute(conf.get('editor_cmd'), post_path)


def version(args):
    """show version"""
    return get_version()


def main():
    try:
        p = ArghParser()
        p.add_commands([init, build, run, deploy, clean, page, post, version])
        p.dispatch()
    except Exception:
        logger.crash()

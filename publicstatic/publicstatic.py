# coding: utf-8

"""public-static - static website builder."""

import glob
import heapq
import http.server
import os
import re
import shutil
import socketserver
import subprocess
import threading
import traceback
import webbrowser
from publicstatic import conf
from publicstatic import const
from publicstatic import builders
from publicstatic import logger
from publicstatic import helpers
from publicstatic import pathes
from publicstatic import source
from publicstatic.cache import Cache


def init(path=None, force=False):
    """Create new website."""
    conf.generate(path, force)
    try:
        src = pathes.proto()
        dest = conf.site()
        existing = helpers.copydir(src, dest, force=force)
        if len(existing):
            message = "some existing files were overwritten" if force else \
                "some existing files were NOT overwritten (use --force " \
                "to overwrite)"
            logger.warn("%s\n- %s" % (message, '\n- '.join(existing)))
        logger.info('website created successfully, have fun!')
    except Exception as ex:
        logger.error('initialization failed: ' + str(ex))
        print(str(ex))


def build(path=None, output=None):
    """Generate web content from source."""
    conf.load(path)
    cache = Cache()
    if cache.processing_errors():
        for file_name, error in cache.processing_errors():
            message = "error processing source file '%s' - %s"
            logger.error(message % (file_name, error))
    if output:
        conf.set('build_path', output)
    logger.info('build directory: ' + conf.get('build_path'))
    for builder in builders.order():
        builder(cache)


def _serve(path, port):
    """Running web server in a background thread."""
    print("running HTTP server on port %d..." % port)
    print('use Ctrl-Break to stop webserver')
    os.chdir(path)
    handler = http.server.SimpleHTTPRequestHandler
    server = socketserver.TCPServer(('', port), handler)
    server.serve_forever()


def run(path=None, port=None, browse=False):
    """Preview generated website."""
    conf.load(path)
    helpers.check_build(conf.get('build_path'))
    port = port or conf.get('port')
    args = [conf.get('build_path'), port]
    threading.Thread(target=_serve, args=args).start()
    if browse:
        url = "http://localhost:%d/" % port
        webbrowser.open_new(url)


def deploy(path=None):
    """Deploy generated website to the remote web server."""
    conf.load(path)
    helpers.check_build(conf.get('build_path'))
    logger.info('deploying website...')
    if not conf.get('deploy_cmd'):
        raise Exception('deploy command is not defined')
    cmd = conf.get('deploy_cmd').format(build_path=conf.get('build_path'))
    try:
        output = subprocess.check_output(cmd.split())
        logger.debug("Command output:\n%s" % output.decode('utf-8'))
        logger.info('done')
    except subprocess.CalledProcessError as e:
        logger.error(e)
        logger.debug("Command output:\n%s" % e.output.decode('utf-8'))


def clean(path=None):
    """Delete all generated content."""
    conf.load(path)
    logger.info('cleaning output...')
    helpers.rmdir(conf.get('build_path'))
    logger.info('done')


def page(path=None, name=None, force=False, edit=False):
    """Create new page."""
    conf.load(path)
    try:
        path = source.PageSource.create(name, force)
    except source.PageExistsException:
        logger.error('page already exists, use -f to overwrite')
        return
    logger.info('page created: ' + path)
    if edit:
        helpers.execute(conf.get('editor_cmd'), path)


def post(path=None, name=None, force=False, edit=False):
    """Create new post."""
    conf.load(path)
    path = source.PostSource.create(name, force)
    logger.info('post created: ' + path)
    if edit:
        helpers.execute(conf.get('editor_cmd'), path)


def theme_update(path=None, safe=False):
    conf.load(path)

    if safe:
        logger.info('saving current theme')
        assets_bak = "%s.bak" % pathes.theme_assets_installed()
        templates_bak = "%s.bak" % pathes.theme_templates_installed()
        try:
            for path in [templates_bak, assets_bak]:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
            shutil.move(pathes.theme_assets_installed(), assets_bak)
            shutil.move(pathes.theme_templates_installed(), templates_bak)
        except Exception as e:
            logger.error('error saving existing theme files: ' + str(e))
            return

    logger.info('updating theme files')
    try:
        path = pathes.theme_assets_source()
        helpers.copydir(path, pathes.theme_assets_installed())
        path = pathes.theme_templates_source()
        helpers.copydir(path, pathes.theme_templates_installed())
    except Exception as e:
        logger.error('error updating theme: ' + str(e))

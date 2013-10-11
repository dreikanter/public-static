# coding: utf-8

"""public-static - static website builder."""

from multiprocessing import Process
import os
import shutil
from publicstatic import conf
from publicstatic import const
from publicstatic import builders
from publicstatic import logger
from publicstatic import helpers
from publicstatic import source
from publicstatic.cache import Cache
from publicstatic.formatter import CustomFormatter
from publicstatic.version import get_version


def init(source=None):
    """create new website"""
    conf.generate(source)
    try:
        helpers.copydir(conf.generic_dir(), conf.site_dir())
        logger.info('website created successfully, have fun!')
    except Exception as ex:
        logger.error('initialization failed: ' + str(ex))
        print(str(ex))


def build(source=None):
    """generate web content from source"""
    conf.load(source)
    cache = Cache()
    for builder in builders.order():
        builder(cache)


def run(source=None, port=None, browse=False):
    """run local web server to preview generated website"""
    conf.load(source)
    helpers.check_build(conf.get('build_path'))
    original_cwd = os.getcwd()
    port = port or conf.get('port')
    logger.info("running HTTP server on port %d..." % port)
    from http.server import SimpleHTTPRequestHandler
    from socketserver import TCPServer
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(('', port), handler)

    try:
        if browse:
            url = "http://localhost:%d/" % port
            logger.info("opening browser in %g seconds" % const.BROWSER_DELAY)
            p = Process(target=helpers.browse, args=(url, const.BROWSER_DELAY))
            p.start()

        logger.info('use Ctrl-Break to stop webserver')
        os.chdir(conf.get('build_path'))
        httpd.serve_forever()

    except KeyboardInterrupt:
        logger.info('server was stopped by user')
    finally:
        os.chdir(original_cwd)


def deploy(source=None):
    """deploy generated website to the remote web server"""
    conf.load(source)
    helpers.check_build(conf.get('build_path'))

    if not conf.get('deploy_cmd'):
        raise Exception('deploy command is not defined')

    logger.info('deploying website...')
    cmd = conf.get('deploy_cmd').format(build_path=conf.get('build_path'))

    from subprocess import call
    call(cmd)

    logger.info('done')


def clean(source=None):
    """delete all generated content"""
    conf.load(source)
    logger.info('cleaning output...')
    helpers.drop_build(conf.get('build_path'))
    logger.info('done')


def page(source=None, name=None, force=False, edit=False):
    """create new page"""
    conf.load(source)
    try:
        path = source.PageSource.create(name, force)
    except source.PageExistsException:
        logger.error('page already exists, use -f to overwrite')
        return
    logger.info('page created: ' + path)
    if edit:
        helpers.execute(conf.get('editor_cmd'), path)


def post(source=None, name=None, force=False, edit=False):
    """create new post"""
    conf.load(source)
    path = source.PostSource.create(name, force)
    logger.info('post created: ' + path)
    if edit:
        helpers.execute(conf.get('editor_cmd'), path)


def update(source=None):
    """update templates to the latest version"""
    conf.load(source)
    site_dir = conf.site_dir()

    def replace(subject, dir_name):
        tmp = dir_name + '_'
        if os.path.isdir(dir_name):
            os.rename(dir_name, tmp)
        path = lambda dirname: os.path.join(dirname, subject)
        helpers.copydir(path(conf.generic_dir()), path(site_dir))
        if os.path.exists(tmp):
            shutil.rmtree(tmp)

    logger.info('updating templates')
    replace(const.TEMPLATES_DIR, conf.get('tpl_path'))
    logger.info('done')


def image_add(source, file_name, id=None):
    pass


def image_rm(source):
    pass


def image_ls(source):
    pass

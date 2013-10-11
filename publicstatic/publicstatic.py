# coding: utf-8

"""public-static - static website builder."""

import glob
import http.server
import os
import PIL
import re
import shutil
import socketserver
import subprocess
import threading
import webbrowser
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
    """Create new website."""
    conf.generate(source)
    try:
        helpers.copydir(conf.generic_dir(), conf.site_dir())
        logger.info('website created successfully, have fun!')
    except Exception as ex:
        logger.error('initialization failed: ' + str(ex))
        print(str(ex))


def build(source=None):
    """Generate web content from source."""
    conf.load(source)
    cache = Cache()
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


def run(source=None, port=None, browse=False):
    """Preview generated website."""
    conf.load(source)
    helpers.check_build(conf.get('build_path'))
    original_cwd = os.getcwd()
    port = port or conf.get('port')
    args = [conf.get('build_path'), port]
    threading.Thread(target=_serve, args=args).start()
    if browse:
        url = "http://localhost:%d/" % port
        webbrowser.open_new(url)


def deploy(source=None):
    """Deploy generated website to the remote web server."""
    conf.load(source)
    helpers.check_build(conf.get('build_path'))
    logger.info('deploying website...')
    if not conf.get('deploy_cmd'):
        raise Exception('deploy command is not defined')
    cmd = conf.get('deploy_cmd').format(build_path=conf.get('build_path'))
    subprocess.call(cmd)
    logger.info('done')


def clean(source=None):
    """Delete all generated content."""
    conf.load(source)
    logger.info('cleaning output...')
    helpers.drop_build(conf.get('build_path'))
    logger.info('done')


def page(source=None, name=None, force=False, edit=False):
    """Create new page."""
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
    """Create new post."""
    conf.load(source)
    path = source.PostSource.create(name, force)
    logger.info('post created: ' + path)
    if edit:
        helpers.execute(conf.get('editor_cmd'), path)


def update(source=None):
    """Update templates to the latest version."""
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


def _image_id():
    pattern = re.compile(r"^(\d+).*")
    last_id = 0
    path = conf.get('images_path')
    for file_name in glob.glob(os.path.join(path, "*_*.*")):
        match = pattern.match(os.path.basename(file_name))
        if match:
            try:
                last_id = max(last_id, int(match.group(1)))
            except:
                pass
    return last_id + 1


def _normalize_image_ext(file_name):
    _, ext = os.path.splitext(os.path.basename(file_name))
    return ext.lower()


def image_add(source, file_name, id=None):
    """Add new image to site sources."""
    conf.load(source)
    if not os.path.exists(file_name):
        logger.error('image not exists')
        return

    images_path = conf.get('images_path')
    if not os.path.isdir(images_path):
        helpers.makedirs(images_path)

    image = PIL.Image.open(file_name)
    width, height = image.size
    parts = {
        'id': _image_id(),
        'width': width,
        'height': height,
        'ext': _normalize_image_ext(file_name),
    }
    original = "{id}_{width}x{height}{ext}".format(**parts)
    dest = os.path.join(images_path, original)
    logger.info("adding image: %s" % original)
    shutil.copyfile(file_name, dest)

    max_width = conf.get('image_max_width') or width
    max_height = conf.get('image_max_height') or height
    ratio = min(max_width/width, max_height/height)
    if ratio < 1:
        size = (int(width * ratio), int(height * ratio))
        image.thumbnail(size, PIL.Image.ANTIALIAS)
        scaled = "{id}_{width}x{height}-preview{ext}".format(**parts)
        dest = os.path.join(images_path, original)
        logger.info("saving scaled image: %s" % scaled)
        image.save(dest)


def image_rm(source):
    # glob *_id_*
    # remove if exists (both, original and scaled)
    pass


def image_ls(source):
    # glob and order by utime
    # show last N
    pass

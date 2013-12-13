# coding: utf-8

"""public-static - static website builder."""

import glob
import heapq
import http.server
import os
import re
import socketserver
import subprocess
import threading
import traceback
import webbrowser
from publicstatic import conf
from publicstatic import const
from publicstatic import builders
from publicstatic import images
from publicstatic import logger
from publicstatic import helpers
from publicstatic import source
from publicstatic.cache import Cache


def init(src_dir=None):
    """Create new website."""
    conf.generate(src_dir)
    try:
        helpers.copydir(conf.proto_dir(), conf.site_dir())
        logger.info('website created successfully, have fun!')
    except Exception as ex:
        logger.error('initialization failed: ' + str(ex))
        print(str(ex))


def build(src_dir=None, def_tpl=False):
    """Generate web content from source."""
    conf.load(src_dir)
    if def_tpl:
        conf.set('default_templates', True)  # overriding parameter
    cache = Cache()
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


def run(src_dir=None, port=None, browse=False):
    """Preview generated website."""
    conf.load(src_dir)
    helpers.check_build(conf.get('build_path'))
    port = port or conf.get('port')
    args = [conf.get('build_path'), port]
    threading.Thread(target=_serve, args=args).start()
    if browse:
        url = "http://localhost:%d/" % port
        webbrowser.open_new(url)


def deploy(src_dir=None):
    """Deploy generated website to the remote web server."""
    conf.load(src_dir)
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


def clean(src_dir=None):
    """Delete all generated content."""
    conf.load(src_dir)
    logger.info('cleaning output...')
    helpers.drop_build(conf.get('build_path'))
    logger.info('done')


def page(src_dir=None, name=None, force=False, edit=False):
    """Create new page."""
    conf.load(src_dir)
    try:
        path = source.PageSource.create(name, force)
    except source.PageExistsException:
        logger.error('page already exists, use -f to overwrite')
        return
    logger.info('page created: ' + path)
    if edit:
        helpers.execute(conf.get('editor_cmd'), path)


def post(src_dir=None, name=None, force=False, edit=False):
    """Create new post."""
    conf.load(src_dir)
    path = source.PostSource.create(name, force)
    logger.info('post created: ' + path)
    if edit:
        helpers.execute(conf.get('editor_cmd'), path)


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


def image_add(src_dir, file_name, id=None):
    """Add new image to site sources."""
    # conf.load(src_dir)
    # if not os.path.exists(file_name):
    #     logger.error('image not exists')
    #     return

    # images_path = conf.get('images_path')
    # if not os.path.isdir(images_path):
    #     helpers.makedirs(images_path)

    # # image = PIL.Image.open(file_name)
    # # width, height = image.size
    # width, height = 0, 0
    # _, ext = os.path.splitext(os.path.basename(file_name))

    # parts = {
    #     'id': _image_id(),
    #     'width': width,
    #     'height': height,
    #     'ext': ext.lower(),
    # }
    # original = "{id}_{width}x{height}{ext}".format(**parts)
    # dest = os.path.join(images_path, original)
    # logger.info("adding image: %s" % original)
    # shutil.copyfile(file_name, dest)

    # max_width = conf.get('image_max_width') or width
    # max_height = conf.get('image_max_height') or height
    # ratio = min(max_width/width, max_height/height)
    # if ratio < 1:
    #     size = (int(width * ratio), int(height * ratio))
    #     image.thumbnail(size, PIL.Image.ANTIALIAS)
    #     scaled = "{id}_{width}x{height}-preview{ext}".format(**parts)
    #     dest = os.path.join(images_path, original)
    #     logger.info("saving scaled image: %s (%0.2f)" % (scaled, ratio))
    #     image.save(dest)


def image_rm(src_dir, id):
    conf.load(src_dir)
    path = conf.get('images_path')
    wildcard = "%s_*.*" % str(id)
    for file_name in glob.glob(os.path.join(path, wildcard)):
        try:
            logger.info("deleting %s" % file_name)
            os.remove(file_name)
        except Exception as e:
            logger.error(str(e))
            logger.debug(traceback.format_exc())


def image_ls(src_dir, number=None):
    conf.load(src_dir)
    number = number or const.LS_NUM
    tail = heapq.nlargest(number, images.all(), key=lambda image: image[0])
    for image in tail:
        print("%d -> %s" % (image[0], image[1]))

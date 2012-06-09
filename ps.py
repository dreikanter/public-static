#!/usr/bin/env python

import os
import os.path
from pprint import pprint, pformat
from configparser import ConfigParser
import shutil
import datetime
import time
import logging
import SimpleHTTPServer
import SocketServer
from multiprocessing import Process
import baker
import markdown
import pystache

__author__ = "Alex Musayev"
__email__ = "alex.musayev@gmail.com"
__copyright__ = "Copyright 2012, %s <http://alex.musayev.com>" % __author__
__license__ = "MIT"
__version_info__ = (0, 0, 1)
__version__ = ".".join(map(str, __version_info__))
__status__ = "Development"
__url__ = "http://github.com/dreikanter/gistopin"

script_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(__name__)
conf = {}

DEFAULT_SECTION = script_name
DEFAULT_CONF = "%s.ini" % script_name
DEFAULT_LOG = "%s.log" % script_name
DEFAULT_PORT = 8000
DEFAULT_BROWSER_OPEN_DELAY = 2.0  # seconds

COMMON_PARAMS = {
    "config": "Configuration file",
    "section": "Configuration file section",
    "logfile": "Log file"
    }

COMMON_SHORTOPS = {
    "config": "c",
    "section": "s",
    "logfile": "l"
    }

TRUE_VALUES = ['1', 'true', 'yes', 'y']
TEMPLATE_FILE_NAME = "%s.mustache.html"
LOG_CONSOLE_FORMAT = ('%(asctime)s %(levelname)s: %(message)s', '%H:%M:%S')
LOG_FILE_FORMAT = ('%(asctime)s %(levelname)s: %(message)s', '%Y/%m/%d %H:%M:%S')


# Initialization =============================================================

def init(conf_file, section, log_file):
    """Gets the configuration values or termanates execution in case of errors"""

    def get_params():
        parser = ConfigParser()
        with open(conf_file, 'rt') as f:
            parser.readfp(f)
        return parser.items(section)

    def get_bool(bool_str):
        return True if bool_str.lower() in TRUE_VALUES else False

    def get_pwd(pwd_str):
        file_prefix = 'file://'
        if pwd_str.startswith(file_prefix):
            with open(pwd_str[len(file_prefix):]) as f:
                return f.readline().strip()
        return pwd_str

    try:
        init_logging(log_file)

    except Exception as e:
        print("Error initializing loggign: " + str(e))
        exit(1)

    try:
        global conf
        conf = {item[0]: item[1] for item in get_params()}
        log.info("Using configuration from %s [%s]" % (conf_file, section))

        conf['pages_path'] = os.path.abspath(conf['pages_path'])
        conf['static_path'] = os.path.abspath(conf['static_path'])
        conf['build_path'] = os.path.abspath(conf['build_path'])
        conf['templates_path'] = os.path.abspath(conf['templates_path'])
        conf['browser_opening_delay'] = float(conf['browser_opening_delay']) if 'browser_opening_delay' in conf else DEFAULT_BROWSER_OPEN_DELAY

        # TODO Check for mandatory parameters

    except Exception as e:
        log.error("Error reading configuration: " + str(e))
        log.error("Use --help parameter for command line help")
        exit(1)


def init_logging(log_file):
    global log
    log.setLevel(logging.DEBUG)

    channel = logging.StreamHandler()
    channel.setLevel(logging.DEBUG)
    channel.setFormatter(logging.Formatter(LOG_CONSOLE_FORMAT[0], LOG_CONSOLE_FORMAT[1]))

    log.addHandler(channel)

    if log_file:
        dir_path = os.path.dirname(log_file)
        if dir_path:
            ensure_dir_exists(dir_path)
        channel = logging.FileHandler(log_file)
        channel.setLevel(logging.DEBUG)
        channel.setFormatter(logging.Formatter(LOG_FILE_FORMAT[0], LOG_FILE_FORMAT[1]))
        log.addHandler(channel)


# Helper functions ============================================================

def joind(d1, d2):
    """Joins two dictionaries"""
    return dict(d1.items() + d2.items())


def ensure_dir_exists(dir_path):
    """Creates directory if it not exists"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def remake_dir(dir_path):
    """Deletes directory contents if it exists or create new one"""
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)


def getext(file_name):
    """Returns file extension w/o leading dot."""
    return os.path.splitext(file_name)[1][1:]


def process_files(root_path):
    """Walk through source files and process one by one."""
    for cur_dir, dirs, files in os.walk(root_path):
        dest_path = os.path.join(conf['build_path'], cur_dir[len(root_path):].strip("\\/"))
        ensure_dir_exists(dest_path)
        for file_name in files:
            source_file = os.path.join(cur_dir, file_name)
            dest_file = get_dest_file_name(source_file)
            log.info(" * " + source_file[len(root_path):].strip("\\/") +
                ((" => %s" % dest_file) if dest_file != os.path.basename(source_file) else ""))
            process_file(source_file, os.path.join(dest_path, dest_file))


def process_file(source_file, dest_file):
    ext = getext(source_file)
    if ext == "md":
        build_page(source_file, dest_file)
    # elif ext == "css" and conf['minify_css']:
    #     pass
    # elif ext == "js" and conf['minify_js']:
    #     pass
    else:
        pass
        shutil.copyfile(source_file, dest_file)


def build_page(source_file, dest_file):
    try:
        page = read_page_source(source_file)
        page['text'] = markdown.markdown(page['text'])

        with open(dest_file, 'wt') as f:
            f.write(pystache.render(get_template(page['template']), page))

    except Exception as e:
        log.error("Error building page: " + str(e))


def read_page_source(source_file):
    # TODO
    return {
    'title': "I'm in space!",
    'utime': datetime.datetime.now(),
    'ctime': datetime.datetime.now(),
    'template': "default",
    'text': """# I'm in space!\n\n"""
            """Dad! I'm in space! I'm proud of you, son. Dad, are you space? Yes. Now we are a family again."""
            """Space space wanna go to space yes please space. Space space. Go to space."""
            """Space space wanna go to space\n\n"""
            """Space space going to space oh boy"""
            """Ba! Ba! Ba ba ba! Space! Ba! Ba! Ba ba ba!"""
            """Oh. Play it cool. Play it cool. Here come the space cops.""",
    }


def get_template(tpl_name):
    file_name = os.path.join(conf['templates_path'], TEMPLATE_FILE_NAME % tpl_name)
    if os.path.exists(file_name):
        with open(file_name, 'rt') as f:
            return f.read()

    raise Exception("Error reading template: %s (%s)" % (tpl_name, file_name))


def get_dest_file_name(source_file):
    """Returns built file name w/o path."""
    base, ext = os.path.splitext(os.path.basename(source_file))
    return base + (".html" if ext == ".md" else ext)


def open_in_browser(url):
    cmd = conf['run_browser_cmd'].replace('{url}', url)
    log.info("Opening browser in %g seconds. Command: [%s]" % (conf['browser_opening_delay'], cmd))
    p = Process(target=bg_open_browser, args=(url, cmd, conf['browser_opening_delay']))
    p.start()


def bg_open_browser(url, cmd, delay):
    """Asyncronously executes default browser with specified URL."""
    try:
        time.sleep(delay)
        print("Executing '%s'" % cmd)
        os.system(cmd)

    except Exception as e:
        print("Error opening browser: " + str(e))


def check_build_is_done():
    """Check if the web content was built and exit if it isn't."""
    if not os.path.isdir(conf['build_path']):
        log.error("Web content directory not exists: [%s]" % conf['build_path'])
        exit(1)


# Baker commands ==============================================================

@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS, default=True)
def build(config=DEFAULT_CONF, section=DEFAULT_SECTION, logfile=DEFAULT_LOG):
    """Generate web content"""
    init(config, section, logfile)

    try:
        remake_dir(conf['build_path'])
        log.info("Building static content from [%s] to [%s]..." % (conf['static_path'], conf['build_path']))
        process_files(conf['static_path'])
        log.info("Building pages from [%s] to [%s]..." % (conf['pages_path'], conf['build_path']))
        process_files(conf['pages_path'])

    except Exception as e:
        log.error("Error: " + str(e))


@baker.command(shortopts=joind(COMMON_SHORTOPS, {"browse": "b", "port": "p"}),
               params=joind(COMMON_PARAMS, {"browse": "Open in default browser", "port": "Port for local HTTP server"}))
def preview(config=DEFAULT_CONF, section=DEFAULT_SECTION, logfile=DEFAULT_LOG, browse=False, port=DEFAULT_PORT):
    '''Run local web server to preview generated web site'''
    init(config, section, logfile)
    check_build_is_done()

    prev_cwd = os.getcwd()
    os.chdir(conf['build_path'])
    log.info("Running HTTP server on port %d..." % port)

    try:
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", port), handler)

        if browse:
            open_in_browser("http://localhost:%s/" % port)

        httpd.serve_forever()

    except KeyboardInterrupt:
        log.info("Server was stopped by user")

    os.chdir(prev_cwd)


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def publish(config=DEFAULT_CONF, section=DEFAULT_SECTION, logfile=DEFAULT_LOG):
    '''Synchronize remote web server with generated content.'''
    init(config, section, logfile)
    check_build_is_done()


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def clean(config=DEFAULT_CONF, section=DEFAULT_SECTION, logfile=DEFAULT_LOG):
    '''Delete all generated web content'''

    init(conf, section, logfile)
    log.info("Cleaning output...")

    try:
        if os.path.exists(conf['build_path']):
            shutil.rmtree(conf['build_path'])
        log.info("Done")

    except Exception as e:
        log.error("Error: " + str(e))


if __name__ == '__main__':
    try:
        baker.run()

    except Exception as e:
        print("Error: " + str(e))
        exit(1)

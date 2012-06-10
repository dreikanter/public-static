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

DEFAULT_CONF = "%s.ini" % script_name
DEFAULT_LOG = "%s.log" % script_name
DEFAULT_PORT = 8000
DEFAULT_BROWSER_OPEN_DELAY = 2.0  # seconds
DEFAULT_PAGES_PATH = './pages'
DEFAULT_STATIC_PATH = './static'
DEFAULT_BUILD_PATH = './www'
DEFAULT_TEMPLATES_PATH = './templates'

# Minification command templates for str.format() function.
# {source} is used in both for source file and {dest} is for processed result.
DEFAULT_MINIFY_JS_CMD = "yuicompressor --type js --nomunge -o {dest} {source}"
DEFAULT_MINIFY_CSS_CMD = "yuicompressor --type css -o {dest} {source}"

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
    def get_params(conf_file, section):
        print("Using configuration from: %s (section: %s)" % (conf_file, section if section else "default"))

        parser = ConfigParser()
        with open(conf_file, 'rt') as f:
            parser.readfp(f)

        if section and not section in parser.sections():
            raise Exception("%s not found" % (("section [%s]" % section) if section else "first section"))

        try:
            section = section if section else parser.sections()[0]
            return {item[0]: item[1] for item in parser.items(section)}
        except:
            raise Exception(("section [%s] not found" % section) if section else "no sections defined")

    def get_bool(bool_str):
        return True if bool_str.lower() in TRUE_VALUES else False

    def get_pwd(pwd_str):
        file_prefix = 'file://'
        if pwd_str.startswith(file_prefix):
            with open(pwd_str[len(file_prefix):]) as f:
                return f.readline().strip()
        return pwd_str

    def init_logging(log_file):
        global log
        log.setLevel(logging.DEBUG)

        channel = logging.StreamHandler()
        channel.setLevel(logging.INFO)
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

    try:
        init_logging(log_file)

    except Exception as e:
        print("Error initializing loggign: " + str(e))
        exit(1)

    try:
        conf = get_params(conf_file, section)

        log.info("Using configuration from %s [%s]" % (conf_file, section))

        conf['pages_path'] = os.path.abspath(conf.get('pages_path', DEFAULT_PAGES_PATH))
        conf['static_path'] = os.path.abspath(conf.get('static_path', DEFAULT_STATIC_PATH))
        conf['build_path'] = os.path.abspath(conf.get('build_path', DEFAULT_BUILD_PATH))
        conf['templates_path'] = os.path.abspath(conf.get('templates_path', DEFAULT_TEMPLATES_PATH))
        conf['browser_opening_delay'] = float(conf.get('browser_opening_delay', DEFAULT_BROWSER_OPEN_DELAY))

        enabled = get_bool(conf.get('minify_js', 'yes'))
        conf['minify_js_cmd'] = conf.get('minify_js_cmd', DEFAULT_MINIFY_JS_CMD) if enabled else None
        
        enabled = get_bool(conf.get('minify_css', 'yes'))
        conf['minify_css_cmd'] = conf.get('minify_css_cmd', DEFAULT_MINIFY_CSS_CMD) if enabled else None

        for param in conf:
            log.debug("%s = [%s]" % (param, conf[param]))

        return conf

    except Exception as e:
        log.critical("Error reading configuration: " + str(e))
        log.info("Use --help parameter for command line help")
        exit(1)


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


def process_files(src_path, build_path, min_js_cmd, min_css_cmd, templates_path):
    """Walk through source files and process one by one."""
    for cur_dir, dirs, files in os.walk(src_path):
        dest_path = os.path.join(build_path, cur_dir[len(src_path):].strip("\\/"))
        ensure_dir_exists(dest_path)

        for file_name in files:
            source_file = os.path.join(cur_dir, file_name)
            dest_file = get_dest_file_name(source_file)

            # log.info(" * " + source_file[len(src_path):].strip("\\/") +
            #     ((" => %s" % dest_file) if dest_file != os.path.basename(source_file) else ""))

            process_file(source_file, os.path.join(dest_path, dest_file), min_css_cmd, min_js_cmd, templates_path)


def process_file(source_file, dest_file, minify_css_cmd, minify_js_cmd, templates_path):
    ext = getext(source_file).lower()
    if ext == "md":
        log.info(" * Building page: " + os.path.basename(source_file))
        build_page(source_file, dest_file, templates_path)

    elif ext == "css" and minify_css_cmd:
        log.info(" * Minifying CSS: " + os.path.basename(source_file))
        execute(minify_css_cmd.format(source=source_file, dest=dest_file))

    elif ext == "js" and minify_js_cmd:
        log.info(" * Minifying JS: " + os.path.basename(source_file))
        execute(minify_js_cmd.format(source=source_file, dest=dest_file))

    else:
        log.info(" * Copying: " + os.path.basename(source_file))
        shutil.copyfile(source_file, dest_file)


def build_page(source_file, dest_file, templates_path):
    try:
        page = read_page_source(source_file)
        page['text'] = markdown.markdown(page['text'])

        with open(dest_file, 'wt') as f:
            f.write(pystache.render(get_template(page['template'], templates_path), page))

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


def get_template(tpl_name, templates_path):
    file_name = os.path.join(templates_path, TEMPLATE_FILE_NAME % tpl_name)
    if os.path.exists(file_name):
        with open(file_name, 'rt') as f:
            return f.read()

    raise Exception("Error reading template: %s (%s)" % (tpl_name, file_name))


def get_dest_file_name(source_file):
    """Returns built file name w/o path."""
    base, ext = os.path.splitext(os.path.basename(source_file))
    return base + (".html" if ext == ".md" else ext)


def open_in_browser(url, run_browser_cmd, browser_opening_delay):
    cmd = run_browser_cmd.format(url=url)
    log.info("Opening browser in %g seconds. Command: [%s]" % (browser_opening_delay, cmd))
    p = Process(target=bg_open_browser, args=(url, cmd, browser_opening_delay))
    p.start()


def bg_open_browser(url, cmd, delay):
    """Asyncronously executes default browser with specified URL."""
    time.sleep(delay)
    execute(cmd)


def execute(cmd):
    """Execute system command."""
    try:
        log.debug("Executing '%s'" % cmd)
        os.system(cmd)

    except Exception as e:
        print("Error executing system command: " + str(e))


def check_build_is_done(build_path):
    """Check if the web content was built and exit if it isn't."""
    if not os.path.isdir(build_path):
        log.critical("Web content directory not exists: [%s]" % build_path)
        exit(1)


# Baker commands ==============================================================

@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS, default=True)
def build(config=DEFAULT_CONF, section=None, logfile=DEFAULT_LOG):
    """Generate web content"""
    conf = init(config, section, logfile)

    try:
        remake_dir(conf['build_path'])
        log.info("Building path: [%s]" % conf['build_path'])
        log.info("Processing static content from [%s]..." % conf['static_path'])
        process_files(conf['static_path'], conf['build_path'], conf['minify_js_cmd'], conf['minify_css_cmd'], conf['templates_path'])
        log.info("Processing pages from [%s]..." % conf['pages_path'])
        process_files(conf['pages_path'], conf['build_path'], conf['minify_js_cmd'], conf['minify_css_cmd'], conf['templates_path'])

    except Exception as e:
        log.critical("Error: " + str(e))


@baker.command(shortopts=joind(COMMON_SHORTOPS, {"browse": "b", "port": "p"}),
               params=joind(COMMON_PARAMS, {"browse": "Open in default browser", "port": "Port for local HTTP server"}))
def preview(config=DEFAULT_CONF, section=None, logfile=DEFAULT_LOG, browse=False, port=DEFAULT_PORT):
    '''Run local web server to preview generated web site'''
    conf = init(config, section, logfile)
    check_build_is_done(conf['build_path'])

    prev_cwd = os.getcwd()
    os.chdir(conf['build_path'])
    log.info("Running HTTP server on port %d..." % port)

    try:
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", port), handler)

        if browse:
            open_in_browser("http://localhost:%s/" % port, conf['run_browser_cmd'], conf['browser_opening_delay'])

        httpd.serve_forever()

    except KeyboardInterrupt:
        log.info("Server was stopped by user")

    os.chdir(prev_cwd)


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def publish(config=DEFAULT_CONF, section=None, logfile=DEFAULT_LOG):
    '''Synchronize remote web server with generated content.'''
    conf = init(config, section, logfile)
    check_build_is_done(conf['build_path'])


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def clean(config=DEFAULT_CONF, section=None, logfile=DEFAULT_LOG):
    '''Delete all generated web content'''
    conf = init(config, section, logfile)
    log.info("Cleaning output...")

    try:
        if os.path.exists(conf['build_path']):
            shutil.rmtree(conf['build_path'])
        log.info("Done")

    except Exception as e:
        log.critical("Error: " + str(e))


if __name__ == '__main__':
    try:
        baker.run()

    except Exception as e:
        print("Error: " + str(e))
        exit(1)

#!/usr/bin/env python

import os
import os.path
import io
import re
import time
import shutil
import codecs
import logging
from datetime import datetime
from multiprocessing import Process
from configparser import RawConfigParser
import baker
import markdown
import pystache


__author__ = "Alex Musayev"
__email__ = "alex.musayev@gmail.com"
__copyright__ = "Copyright 2012, %s <http://alex.musayev.com>" % __author__
__license__ = "MIT"
__version_info__ = (0, 2, 0)
__version__ = ".".join(map(str, __version_info__))
__status__ = "Development"
__url__ = "http://github.com/dreikanter/public-static"


SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
DEFAULT_CONF = "%s.ini" % SCRIPT_NAME
DEFAULT_LOG = "%s.log" % SCRIPT_NAME

CONF = {
    # Default port value (overridable with command line param)
    'port': '8000',

    # Amount of seconds between starting local web server
    # and opening a browser
    'browser_opening_delay': '2.0',

    'pages_path': './pages',
    'static_path': './static',
    'build_path': './www',
    'templates_path': './templates',

    # Default template neme (overridable with page header 'template' parameter)
    'template': 'default',

    # Default author name (overridable with page header 'author' parmeter)
    'author': '',

    'minify_js': 'y',
    'minify_css': 'y',

    # Minification command templates for str.format() function.
    # {source} is used in both for source file and {dest} is for processed result.
    'minify_js_cmd': "yuicompressor --type js --nomunge -o {dest} {source}",
    'minify_css_cmd': "yuicompressor --type css -o {dest} {source}",

    'publish_cmd': '',
    'generator': "{name} {version}",
}

COMMON_PARAMS = {
    "config": "Configuration file",
    "section": "Configuration file section",
    "logfile": "Log file",
    "verbose": "Enable detailed logging"
}

COMMON_SHORTOPS = {
    "config": "c",
    "section": "s",
    "logfile": "l",
    "verbose": "v"
}

TRUE_VALUES = ['1', 'true', 'yes', 'y']
TEMPLATE_FILE_NAME = "%s.mustache.html"
LOG_CONSOLE_FORMAT = ('%(asctime)s %(levelname)s: %(message)s', '%H:%M:%S')
LOG_FILE_FORMAT = ('%(asctime)s %(levelname)s: %(message)s', '%Y/%m/%d %H:%M:%S')
TIME_FORMAT = "%Y/%m/%d %H:%M:%S"
RE_FLAGS = re.I | re.M | re.U
PARAM_PATTERN = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", RE_FLAGS)
MD = markdown.Markdown(extensions=['nl2br', 'grid'])

log = logging.getLogger(SCRIPT_NAME)
conf = {}


# Initialization =============================================================

def init(conf_file, section, log_file, verbose=False):
    """Gets the configuration values."""
    init_logging(log_file, verbose)

    try:
        global conf
        conf = CONF
        log.info("Using configuration from %s [%s]" % (conf_file, section))

        conf.update(get_params(conf_file, section))
        purify_conf()
        verify_conf()

        from pprint import pprint
        pprint(conf)

        # Dumping configuration to debug log
        for param in conf:
            log.debug("%s = [%s]" % (param, conf[param]))
    except Exception as e:
        log.exception("Error reading configuration")
        log.info("Use --help parameter for command line help")
        exit(1)


def init_logging(log_file, verbose):
    try:
        global log
        log.setLevel(logging.DEBUG)

        channel = logging.StreamHandler()
        channel.setLevel(logging.DEBUG if verbose else logging.INFO)
        fmt = logging.Formatter(LOG_CONSOLE_FORMAT[0], LOG_CONSOLE_FORMAT[1])
        channel.setFormatter(fmt)
        log.addHandler(channel)

        if log_file:
            ensure_dir_exists(os.path.dirname(log_file))
            channel = logging.FileHandler(log_file)
            channel.setLevel(logging.DEBUG)
            fmt = logging.Formatter(LOG_FILE_FORMAT[0], LOG_FILE_FORMAT[1])
            channel.setFormatter(fmt)
            log.addHandler(channel)
    except Exception as e:
        print("Error initializing loggign: " + str(e))
        exit(1)


def purify_conf():
    """Updates configuration parameters requiring processing."""
    conf['pages_path'] = os.path.abspath(conf['pages_path'])
    conf['static_path'] = os.path.abspath(conf['static_path'])
    conf['build_path'] = os.path.abspath(conf['build_path'])
    conf['templates_path'] = os.path.abspath(conf['templates_path'])
    conf['browser_opening_delay'] = float(conf['browser_opening_delay'])
    conf['generator'] = conf['generator'].strip().format(name=SCRIPT_NAME, version=__version__)
    conf['minify_js'] = get_bool(conf['minify_js'])
    conf['minify_css'] = get_bool(conf['minify_css'])
    conf['minify_js_cmd'] = conf['minify_js_cmd'].strip()
    conf['minify_css_cmd'] = conf['minify_css_cmd'].strip()
    conf['publish_cmd'] = conf['publish_cmd'].strip()
    conf['port'] = int(conf['port'])


def verify_conf():
    """Checks if configuration is correct."""
    if conf['minify_js'] and not conf['minify_js_cmd']:
        log.warn("JS minification enabled but [minify_js_cmd] is not defined by configuration.")
    if conf['minify_css'] and not conf['minify_css_cmd']:
        log.warn("CSS minification enabled but [minify_css_cmd] is not defined by configuration.")
    if not conf['publish_cmd']:
        log.warn("Publishing command (publish_cmd) is not defined by configuration.")


# Website building ============================================================

def process_files():
    """Walk through source files and process one by one."""
    process_dir("static files", conf['static_path'])
    process_dir("pages", conf['pages_path'])


def process_dir(message, source_root):
    log.info("Processing %s from [%s]..." % (message, source_root))

    for cur_dir, dirs, files in os.walk(source_root):
        rel_path = cur_dir[len(source_root):].strip("\\/")
        dest_path = os.path.join(conf['build_path'], rel_path)
        ensure_dir_exists(dest_path)

        for file_name in files:
            process_file(source_root, os.path.join(cur_dir, file_name))


def process_file(source_root, source_file):
    """Process single file."""
    rel_source = os.path.relpath(source_file, source_root)
    base, ext = os.path.splitext(rel_source)
    rel_dest = base + ('.html' if ext == '.md' else ext)
    dest_file = os.path.join(conf['build_path'], rel_dest)

    if ext == '.md':
        log.info(" * Building page: %s => %s" % (rel_source, rel_dest))
        build_page(source_file, dest_file, conf['templates_path'])

    elif ext == '.css' and conf['minify_css'] and conf['minify_css_cmd']:
        log.info(' * Minifying CSS: ' + rel_source)
        execute(conf['minify_css_cmd'].format(source=source_file, dest=dest_file))

    elif ext == '.js' and conf['minify_js'] and conf['minify_js_cmd']:
        log.info(' * Minifying JS: ' + rel_source)
        execute(conf['minify_js_cmd'].format(source=source_file, dest=dest_file))

    else:
        log.info(' * Copying: ' + rel_source)
        shutil.copyfile(source_file, dest_file)


def build_page(source_file, dest_file, templates_path):
    """Builds a page from markdown source amd mustache template."""
    try:
        page = read_page_source(source_file)
        with codecs.open(dest_file, mode='w', encoding='utf8') as f:
            f.write(pystache.render(get_template(page['template'], templates_path), page))
    except Exception as e:
        log.exception("Content processing error")


def read_page_source(source_file):
    """Reads a page file to dictionary.

    TODO: Describe page format here."""
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

        page['title'] = page.get('title', get_md_h1(page['content'])).strip()
        page['template'] = page.get('template', conf['template']).strip()
        page['author'] = page.get('author', conf['author']).strip()
        page['content'] = MD.convert(page.get('content', '').strip())

        # Take date/time from file system if not explicitly defined
        purify_time(page, 'ctime', os.path.getctime(source_file))
        purify_time(page, 'mtime', os.path.getmtime(source_file))

        return page

    except Exception as e:
        log.exception("Page source parsing error [%s]" % source_file)
        return {}


def get_template(tpl_name, templates_path):
    file_name = os.path.join(templates_path, TEMPLATE_FILE_NAME % tpl_name)
    if os.path.exists(file_name):
        with codecs.open(file_name, mode='r', encoding='utf8') as f:
            return f.read()

    raise Exception("Error reading template: %s (%s)" % (tpl_name, file_name))


# General helpers =============================================================

def get_params(conf_file, section):
    print("Configuration: %s [%s]" % (conf_file, section or "default"))

    parser = RawConfigParser()
    with codecs.open(conf_file, mode='r', encoding='utf8') as f:
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
        with open(pwd_str[len(file_prefix):], 'rt') as f:
            return f.readline().strip()
    return pwd_str


def joind(d1, d2):
    """Joins two dictionaries"""
    return dict(d1.items() + d2.items())


def ensure_dir_exists(dir_path):
    """Creates directory if it not exists"""
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)


def execute(cmd):
    """Execute system command."""
    try:
        log.debug("Executing '%s'" % cmd)
        os.system(cmd)

    except Exception as e:
        print("Error executing system command: " + str(e))


def delayed_execute(cmd, delay):
    """This function intended to execute system command asyncronously."""
    time.sleep(delay)
    execute(cmd)


def check_build_is_done(build_path):
    """Check if the web content was built and exit if it isn't."""
    if not os.path.isdir(build_path):
        log.exception("Web content directory not exists: [%s]" % build_path)
        exit(1)


def drop_build_dir(build_path, create_new=False):
    """Drops the build if it exists."""
    if os.path.isdir(build_path):
        shutil.rmtree(build_path, ignore_errors=True)
    if create_new and not os.path.isdir(build_path):
        os.makedirs(build_path)


def get_md_h1(text):
    """Extracts the first h1-header from markdown text."""
    matches = re.search(r"^\s*#\s*(.*)\s*", text, RE_FLAGS)
    return matches.group(1) if matches else ""


def purify_time(page, time_parm, default):
    """Returns time value from page dict. If there is no
    specified value, default will be returned."""
    if time_parm in page:
        page[time_parm] = time.strptime(page[time_parm], TIME_FORMAT)
    else:
        page[time_parm] = datetime.fromtimestamp(default)


# Baker commands ==============================================================

@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS, default=True)
def build(config=DEFAULT_CONF, section=None, logfile=DEFAULT_LOG, verbose=False):
    """Generate web content"""
    init(config, section, logfile, verbose)

    try:
        drop_build_dir(conf['build_path'])
        log.info("Building path: [%s]" % conf['build_path'])
        process_files()
        log.info("Done")
    except Exception as e:
        log.exception(e)


@baker.command(shortopts=joind(COMMON_SHORTOPS, {"browse": "b", "port": "p"}),
               params=joind(COMMON_PARAMS, {"browse": "Open in default browser", "port": "Port for local HTTP server"}))
def preview(config=DEFAULT_CONF, section=None, logfile=DEFAULT_LOG, verbose=False, browse=False, port=None):
    """Run local web server to preview generated web site"""
    init(config, section, logfile, verbose)

    check_build_is_done(conf['build_path'])
    prev_cwd = os.getcwd()
    os.chdir(conf['build_path'])
    port = port or conf['port']
    log.info("Running HTTP server on port %d..." % port)

    try:
        import SimpleHTTPServer
        import SocketServer

        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", port), handler)

        if browse:
            cmd = conf['run_browser_cmd'].format(url=("http://localhost:%s/" % port))
            log.info("Opening browser in %g seconds. Command: [%s]" % (conf['browser_opening_delay'], cmd))
            log.info("Use Ctrl-Break to stop webserver")
            p = Process(target=delayed_execute, args=(cmd, conf['browser_opening_delay']))
            p.start()

        httpd.serve_forever()

    except KeyboardInterrupt:
        log.info("Server was stopped by user")
    finally:
        os.chdir(prev_cwd)


# TODO: Add --dry-run mode.
@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def publish(config=DEFAULT_CONF, section=None, logfile=DEFAULT_LOG, verbose=False):
    """Synchronize remote web server with generated content."""
    init(config, section, logfile, verbose)
    check_build_is_done(conf['build_path'])

    if conf['publish_cmd']:
        try:
            log.info("Publishing...")
            execute(conf['publish_cmd'].format(path=conf['build_path']))
            log.info("Done")
        except Exception as e:
            log.exception("Publishing error")
    else:
        log.error("Publishing command (publish_cmd) is not defined by configuration")


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def clean(config=DEFAULT_CONF, section=None, logfile=DEFAULT_LOG, verbose=False):
    """Delete all generated web content"""
    init(config, section, logfile, verbose)

    try:
        log.info("Cleaning output...")
        drop_build_dir(conf['build_path'])
        log.info("Done")
    except Exception as e:
        log.exception(e)


if __name__ == '__main__':
    try:
        baker.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(1)

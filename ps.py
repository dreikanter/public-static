#!/usr/bin/env python

import os
import os.path
import io
import re
import time
import shutil
import codecs
import logging
import traceback
from datetime import datetime
from configparser import RawConfigParser
from multiprocessing import Process
import baker
import markdown
import pystache


__author__ = 'Alex Musayev'
__email__ = 'alex.musayev@gmail.com'
__copyright__ = "Copyright 2012, %s <http://alex.musayev.com>" % __author__
__license__ = 'MIT'
__version_info__ = (0, 4, 0)
__version__ = '.'.join(map(str, __version_info__))
__status__ = 'Development'
__url__ = 'http://github.com/dreikanter/public-static'


SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
DEFAULT_LOG = 'build.log'
DEFAULT_CONF = 'build.conf'

CONF = {
    'generator': "{name} {version}",
    'pages_path': './pages',
    'static_path': './static',
    'build_path': './www',
    'templates_path': './templates',

    # Default port value (overridable with command line param)
    'port': '8000',

    # Amount of seconds between starting local web server
    # and opening a browser
    'browser_opening_delay': '2.0',

    # Default template neme (overridable with page header 'template' parameter)
    'template': 'default',

    # Default author name (overridable with page header 'author' parmeter)
    'author': '',

    'minify_js': 'y',
    'minify_css': 'y',
    'minify_less': 'y',

    # Minification commands: {source} is used in both for source file
    # and {dest} is for processed output
    'minify_js_cmd': "yuicompressor --type js --nomunge -o {dest} {source}",
    'minify_css_cmd': "yuicompressor --type css -o {dest} {source}",

    # Command to sync build_path to web server
    'publish_cmd': '',

    # LESS compiler command ({source} and {dest} will be replaced)
    'less_cmd': "lessc -x {source} > {dest}",
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
TEMPLATE_FILE_NAME = "%s.mustache"
LOG_CONSOLE_FMT = ('%(asctime)s %(levelname)s: %(message)s', '%H:%M:%S')
LOG_FILE_FMT = ('%(asctime)s %(levelname)s: %(message)s', '%Y/%m/%d %H:%M:%S')
TIME_FMT = "%Y/%m/%d %H:%M:%S"
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
    except Exception as e:
        log.debug(traceback.format_exc())
        raise Exception(getxm('Configuration parsing failed', e))


def init_logging(log_file, verbose):
    try:
        global log
        log.setLevel(logging.DEBUG)

        channel = logging.StreamHandler()
        channel.setLevel(logging.DEBUG if verbose else logging.INFO)
        fmt = logging.Formatter(LOG_CONSOLE_FMT[0], LOG_CONSOLE_FMT[1])
        channel.setFormatter(fmt)
        log.addHandler(channel)

        if log_file:
            ensure_dir_exists(os.path.dirname(log_file))
            channel = logging.FileHandler(log_file)
            channel.setLevel(logging.DEBUG)
            fmt = logging.Formatter(LOG_FILE_FMT[0], LOG_FILE_FMT[1])
            channel.setFormatter(fmt)
            log.addHandler(channel)
    except Exception as e:
        log.debug(traceback.format_exc())
        raise Exception(getxm('Logging initialization failed', e))


def purify_conf():
    """Updates configuration parameters requiring processing."""
    conf['pages_path'] = os.path.abspath(conf['pages_path'])
    conf['static_path'] = os.path.abspath(conf['static_path'])
    conf['build_path'] = os.path.abspath(conf['build_path'])
    conf['templates_path'] = os.path.abspath(conf['templates_path'])
    conf['browser_opening_delay'] = float(conf['browser_opening_delay'])
    gen = conf['generator'].strip()
    conf['generator'] = gen.format(name=SCRIPT_NAME, version=__version__)
    conf['minify_js'] = get_bool(conf['minify_js'])
    conf['minify_css'] = get_bool(conf['minify_css'])
    conf['minify_less'] = get_bool(conf['minify_less'])
    conf['minify_js_cmd'] = conf['minify_js_cmd'].strip()
    conf['minify_css_cmd'] = conf['minify_css_cmd'].strip()
    conf['publish_cmd'] = conf['publish_cmd'].strip()
    conf['port'] = int(conf['port'])


def verify_conf():
    """Checks if configuration is correct."""
    if conf['minify_js'] and not conf['minify_js_cmd']:
        log.warn("JS minification enabled but 'minify_js_cmd' is undefined.")
    if conf['minify_less'] or conf['minify_css'] and not conf['minify_css_cmd']:
        log.warn("CSS minification enabled but 'minify_css_cmd' is undefined.")
    if not conf['publish_cmd']:
        log.warn("Publishing command 'publish_cmd' is undefined.")
    if not conf['less_cmd']:
        log.warn("LESS processing command 'less_cmd' is undefined.")


# Website building ============================================================

def process_files():
    """Walk through source files and process one by one."""
    process_dir('static files', conf['static_path'])
    process_dir('pages', conf['pages_path'])


def process_dir(message, source_root):
    log.info("Processing %s from '%s'..." % (message, source_root))

    for cur_dir, dirs, files in os.walk(source_root):
        rel_path = cur_dir[len(source_root):].strip("\\/")
        dest_path = os.path.join(conf['build_path'], rel_path)
        ensure_dir_exists(dest_path)

        for file_name in files:
            process_file(source_root, os.path.join(cur_dir, file_name))


def process_file(source_root, source_file):
    """Process single file.

    Arguments:
        source_root -- root files directory (e.g. 'pages').
        source_file -- source file abs path to process."""
    rel_source = os.path.relpath(source_file, source_root)
    base, ext = os.path.splitext(rel_source)

    new_ext = {
        '.md': '.html',
        '.less': '.css',
    }

    rel_dest = base + (new_ext[ext] if ext in new_ext else ext)
    dest_file = os.path.join(conf['build_path'], rel_dest)

    if ext == '.md':
        log.info(" * Building page: %s => %s" % (rel_source, rel_dest))
        build_page(source_file, dest_file, conf['templates_path'])

    elif ext == '.less':
        log.info(' * Compiling LESS: ' + rel_source)
        if conf['minify_less']:
            tmp_file = dest_file + '.tmp'
            execute_proc('less_cmd', source_file, tmp_file)
            execute_proc('minify_css_cmd', tmp_file, dest_file)
            os.remove(tmp_file)
        else:
            cmd = conf['less_cmd'].format(source=source_file, dest=dest_file)
            execute(cmd)

    elif ext == '.css' and conf['minify_css'] and conf['minify_css_cmd']:
        log.info(' * Minifying CSS: ' + rel_source)
        execute_proc('minify_css_cmd', source_file, dest_file)

    elif ext == '.js' and conf['minify_js'] and conf['minify_js_cmd']:
        log.info(' * Minifying JS: ' + rel_source)
        execute_proc('minify_js_cmd', source_file, dest_file)

    else:
        log.info(' * Copying: ' + rel_source)
        shutil.copyfile(source_file, dest_file)


def build_page(source_file, dest_file, templates_path):
    """Builds a page from markdown source amd mustache template."""
    try:
        page = read_page_source(source_file)
        with codecs.open(dest_file, mode='w', encoding='utf8') as f:
            tpl = get_template(page['template'], templates_path)
            f.write(pystache.render(tpl, page))
    except Exception as e:
        log.debug(traceback.format_exc())
        log.error('Content processing error')


def read_page_source(source_file):
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

        page['title'] = page.get('title', get_md_h1(page['content'])).strip()
        page['template'] = page.get('template', conf['template']).strip()
        page['author'] = page.get('author', conf['author']).strip()
        page['content'] = MD.convert(page.get('content', '').strip())

        # Take date/time from file system if not explicitly defined
        purify_time(page, 'ctime', os.path.getctime(source_file))
        purify_time(page, 'mtime', os.path.getmtime(source_file))

        return page

    except Exception as e:
        log.debug(traceback.format_exc())
        log.error("Page source parsing error '%s'" % source_file)
        return {}


def get_template(tpl_name, templates_path):
    """Gets template file contents.

    Arguments:
        tpl_name -- template name (will be complemented
            to file name using TEMPLATE_FILE_NAME).
        templates_path -- template files path."""
    file_name = os.path.join(templates_path, TEMPLATE_FILE_NAME % tpl_name)
    if os.path.exists(file_name):
        with codecs.open(file_name, mode='r', encoding='utf8') as f:
            return f.read()

    raise Exception("Template not exists: '%s'" % file_name)


# General helpers =============================================================

def getxm(message, exception):
    """Returns annotated exception messge."""
    return ("%s: %s" % (message, str(exception))) if exception else message


def get_params(conf_file, section):
    parser = RawConfigParser()
    with codecs.open(conf_file, mode='r', encoding='utf8') as f:
        parser.readfp(f)

    if section and not section in parser.sections():
        sect = ("section '%s'" % section) if section else 'first section'
        raise Exception("%s not found" % sect)

    try:
        section = section if section else parser.sections()[0]
        return {item[0]: item[1] for item in parser.items(section)}
    except:
        log.debug(traceback.format_exc())
        message = section and ("section '%s' not found" % section)
        raise Exception(message or 'no sections defined')


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


def execute_proc(cmd_name, source, dest):
    """Executes one of the preconfigured commands
    with {source} and {dest} parameters replacement."""
    cmd = conf[cmd_name].format(source=source, dest=dest)
    execute(cmd)


def execute(cmd):
    """Execute system command."""
    try:
        log.debug("Executing '%s'" % cmd)
        os.system(cmd)
    except:
        log.debug(traceback.format_exc())
        log.error('Error executing system command')


def delayed_execute(cmd, delay):
    """This function intended to execute system command asyncronously."""
    time.sleep(delay)
    execute(cmd)


def check_build_is_done(build_path):
    """Check if the web content was built and exit if it isn't."""
    if not os.path.isdir(build_path):
        raise Exception("Web content directory not exists: '%s'" % build_path)


def drop_build_dir(build_path, create_new=False):
    """Drops the build if it exists."""
    if os.path.isdir(build_path):
        shutil.rmtree(build_path, ignore_errors=True)
    if create_new and not os.path.isdir(build_path):
        os.makedirs(build_path)


def get_md_h1(text):
    """Extracts the first h1-header from markdown text."""
    matches = re.search(r"^\s*#\s*(.*)\s*", text, RE_FLAGS)
    return matches.group(1) if matches else ''


def purify_time(page, time_parm, default):
    """Returns time value from page dict. If there is no
    specified value, default will be returned."""
    if time_parm in page:
        page[time_parm] = time.strptime(page[time_parm], TIME_FMT)
    else:
        page[time_parm] = datetime.fromtimestamp(default)


# Baker commands ==============================================================

@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS, default=True)
def build(config=DEFAULT_CONF, section=None,
          logfile=DEFAULT_LOG, verbose=False):
    """Generate web content"""
    init(config, section, logfile, verbose)
    drop_build_dir(conf['build_path'])
    log.info("Building path: '%s'" % conf['build_path'])
    process_files()
    log.info("Build succeeded.")


@baker.command(shortopts=joind(COMMON_SHORTOPS, {
                    'browse': 'b',
                    'port': 'p'
                }),
               params=joind(COMMON_PARAMS, {
                    'browse': 'Open in default browser',
                    'port': 'Port for local HTTP server'
                }))
def preview(config=DEFAULT_CONF, section=None, logfile=DEFAULT_LOG,
            verbose=False, browse=False, port=None):
    """Run local web server to preview generated web site"""
    init(config, section, logfile, verbose)
    check_build_is_done(conf['build_path'])
    original_cwd = os.getcwd()
    port = port or conf['port']
    log.info("Running HTTP server on port %d..." % port)

    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from SocketServer import TCPServer
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(('', port), handler)

    try:
        if browse:
            url = "http://localhost:%s/" % port
            cmd = conf['run_browser_cmd'].format(url=url)
            delay = conf['browser_opening_delay']

            log.info("Opening browser in %g seconds." % delay)
            log.info('Use Ctrl-Break to stop webserver')
            log.debug(" Command: '%s'" % cmd)

            os.chdir(conf['build_path'])
            p = Process(target=delayed_execute, args=(cmd, delay))
            p.start()

        httpd.serve_forever()

    except KeyboardInterrupt:
        log.info('Server was stopped by user')
    finally:
        if browse:
            os.chdir(original_cwd)


# TODO: Add --dry-run mode.
@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def publish(config=DEFAULT_CONF, section=None,
            logfile=DEFAULT_LOG, verbose=False):
    """Synchronize remote web server with generated content."""
    init(config, section, logfile, verbose)
    check_build_is_done(conf['build_path'])

    if not conf['publish_cmd']:
        raise Exception('Publishing command is not defined by configuration')

    log.info('Publishing...')
    execute(conf['publish_cmd'].format(path=conf['build_path']))
    log.info('Done')


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def clean(config=DEFAULT_CONF, section=None,
          logfile=DEFAULT_LOG, verbose=False):
    """Delete all generated web content"""
    init(config, section, logfile, verbose)
    log.info('Cleaning output...')
    drop_build_dir(conf['build_path'])
    log.info('Done')


if __name__ == '__main__':
    try:
        baker.run()
    except Exception as e:
        message = str(e)
        if log:
            log.error(message)
        else:
            print(message)
        exit(1)

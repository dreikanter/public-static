#!/usr/bin/env python
# coding: utf-8

import os
import re
import sys
import time
import shutil
import errno
import codecs
import logging
import traceback
from argh import ArghParser, arg
from datetime import datetime
from multiprocessing import Process
import markdown
# from pprint import pprint
import pystache
import yaml
import authoring

__author__ = authoring.AUTHOR
__email__ = authoring.EMAIL
__copyright__ = authoring.COPYRIGHT
__license__ = authoring.LICENSE
__version_info__ = authoring.VERSION_INFO
__version__ = authoring.VERSION
__status__ = authoring.STATUS
__url__ = authoring.URL

NAME = os.path.splitext(os.path.basename(__file__))[0]
DEFAULT_LOG = '%s.log' % NAME
DEFAULT_CONF = '%s.conf' % NAME
GENERIC_PATH = 'generic-site'
GENERIC_PAGES = 'generic-pages'

CONF = {
    'generator': "%s {version}" % NAME,
    'conf': '',
    'pages_path': 'pages',
    'static_path': 'static',
    'build_path': 'www',
    'templates_path': 'templates',

    # Default port value (overridable with command line param)
    'port': 8000,

    # Amount of seconds between starting local web server
    # and opening a browser
    'browser_opening_delay': 2.0,

    # Default template name (overridable with page header 'template' parameter)
    'template': 'default',

    # Default author name (overridable with page header 'author' parmeter)
    'author': '',

    'minify_js': True,
    'minify_css': True,
    'minify_less': True,

    # Minification commands: {source} is used in both for source file
    # and {dest} is for processed output
    'minify_js_cmd': "yuicompressor --type js --nomunge -o {dest} {source}",
    'minify_css_cmd': "yuicompressor --type css -o {dest} {source}",

    # Command to sync build_path to web server
    'sync_cmd': '',

    # Command to open an URL with a web browser
    'run_browser_cmd': "start {url}",

    # LESS compiler command ({source} and {dest} will be replaced)
    'less_cmd': "lessc -x {source} > {dest}",

    # A list of markdown extensions
    'markdown_extensions': ['nl2br', 'grid', 'smartypants'],

    # Text editor command (use {file} for file name to edit)
    'editor_cmd': "$EDITOR '{file}'",
}

TEMPLATE_FILE_NAME = "%s.mustache"
LOG_CONSOLE_FMT = ("%(asctime)s %(levelname)s: %(message)s", "%H:%M:%S")
LOG_FILE_FMT = ("%(asctime)s %(levelname)s: %(message)s", "%Y/%m/%d %H:%M:%S")
TIME_FMT = "%Y/%m/%d %H:%M:%S"
RE_FLAGS = re.I | re.M | re.U
PARAM_PATTERN = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", RE_FLAGS)
H1_PATTERN = re.compile(r"^\s*#\s*(.*)\s*", RE_FLAGS)

log = logging.getLogger(__name__)
conf = {}


# Initialization =============================================================

def setup(args):
    """Initializes website configuration from command line arguments. Creates
    new site directory if init is True, or reads specified configuration file
    otherwise."""
    config = conf_name(args.path)
    init_logging(args.log, args.verbose)

    global conf

    if args.function == init:
        try:
            site_path = os.path.dirname(config)
            if os.path.isdir(site_path):
                log.error("directory already exists: '%s'" % site_path)
                exit()

            log.info("creating new website at '%s'" % site_path)
            spawn_generic(site_path)

            text = yaml.dump(CONF, width=80, indent=4, default_flow_style=False)
            with codecs.open(config, mode='w', encoding='utf8') as f:
                f.write(text)
            conf = purify_conf(CONF)
        except:
            log.error('initialization failed')
            raise
    else:
        try:
            log.info("loading website configuration from '%s'" % config)
            conf = purify_conf(get_params(config))
        except:
            log.error('configuration failed')
            raise


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
    except:
        logging.error('logging initialization failed')
        raise


def get_params(config):
    """Reads configuration file section to a dictionary"""
    with codecs.open(config, mode='r', encoding='utf8') as f:
        loaded = yaml.load(f.read())

    conf = CONF
    conf.update(dict((item, loaded[item]) for item in loaded))
    conf['conf'] = config
    return conf


def purify_conf(conf):
    """Preprocess configuration parameters"""
    config = conf['conf']
    conf['pages_path'] = get_conf_path(config, conf['pages_path'])
    conf['static_path'] = get_conf_path(config, conf['static_path'])
    conf['build_path'] = get_conf_path(config, conf['build_path'])
    conf['templates_path'] = get_conf_path(config, conf['templates_path'])
    conf['browser_opening_delay'] = float(conf['browser_opening_delay'])
    conf['generator'] = conf['generator'].strip().format(version=__version__)
    conf['minify_js_cmd'] = conf['minify_js_cmd'].strip()
    conf['minify_css_cmd'] = conf['minify_css_cmd'].strip()
    conf['sync_cmd'] = conf['sync_cmd'].strip()
    conf['run_browser_cmd'] = conf['run_browser_cmd'].strip()
    conf['port'] = int(conf['port'])
    return conf


# TODO: Consider to implement verify command for this
# def verify_conf(conf):
#     """Checks if configuration is correct."""
#     if conf['minify_js'] and not conf['minify_js_cmd']:
#         log.warn("JS minification enabled but 'minify_js_cmd' is undefined.")
#     if (conf['minify_less'] or conf['minify_css']) and not conf['minify_css_cmd']:
#         log.warn("CSS minification enabled but 'minify_css_cmd' is undefined.")
#     if not conf['sync_cmd']:
#         log.warn("Synchronization command 'sync_cmd' is undefined.")
#     if not conf['less_cmd']:
#         log.warn("LESS processing command 'less_cmd' is undefined.")
#     return conf


# Website building ============================================================

def process_files():
    """Walk through source files and process one by one"""
    process_dir('static files', conf['static_path'])
    process_dir('pages', conf['pages_path'])


def process_dir(message, source_root):
    log.info("processing %s from '%s'..." % (message, source_root))

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
        log.info("  building page: %s => %s" % (rel_source, rel_dest))
        build_page(source_file, dest_file, conf['templates_path'])

    elif ext == '.less':
        log.info('  compiling LESS: ' + rel_source)
        if conf['minify_less']:
            tmp_file = dest_file + '.tmp'
            execute_proc('less_cmd', source_file, tmp_file)
            execute_proc('minify_css_cmd', tmp_file, dest_file)
            os.remove(tmp_file)
        else:
            execute_proc('less_cmd', source_file, dest_file)

    elif ext == '.css' and conf['minify_css'] and conf['minify_css_cmd']:
        log.info('  minifying CSS: ' + rel_source)
        execute_proc('minify_css_cmd', source_file, dest_file)

    elif ext == '.js' and conf['minify_js'] and conf['minify_js_cmd']:
        log.info('  minifying JS: ' + rel_source)
        execute_proc('minify_js_cmd', source_file, dest_file)

    elif os.path.basename(rel_source) == 'humans.txt':
        log.info('  copying: %s (updated)' % rel_source)
        update_humans(source_file, dest_file)

    else:
        log.info('  copying: ' + rel_source)
        shutil.copyfile(source_file, dest_file)


def build_page(source_file, dest_file, templates_path):
    """Builds a page from markdown source amd mustache template"""
    try:
        page = read_page_source(source_file)
        with codecs.open(dest_file, mode='w', encoding='utf8') as f:
            tpl = get_template(page['template'], templates_path)
            f.write(pystache.render(tpl, page))
    except Exception as e:
        log.debug(traceback.format_exc())
        log.error('content processing error: ' + str(e))


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
        page['content'] = md(page.get('content', ''))

        # Take date/time from file system if not explicitly defined
        purify_time(page, 'ctime', os.path.getctime(source_file))
        purify_time(page, 'mtime', os.path.getmtime(source_file))

        return page

    except:
        log.debug(traceback.format_exc())
        log.error("page processing error '%s'" % source_file)
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

    raise Exception("template not exists: '%s'" % file_name)


# General helpers =============================================================

def conf_name(path):
    """Returns configuration file full path from specified
    command line parameter value"""
    return os.path.abspath(os.path.join(path, DEFAULT_CONF))


def getxm(message, exception):
    """Returns annotated exception messge"""
    return ("%s: %s" % (message, str(exception))) if exception else message


def str2int(value, default=None):
    """Safely converts string value to integer. Returns
    default value if the first argument is not numeric.
    Whitespaces are ok."""
    if type(value) is not int:
        value = str(value).strip()
        value = int(value) if value.isdigit() else default
    return value


def joind(d1, d2):
    """Joins two dictionaries"""
    return dict(d1.items() + d2.items())


def ensure_dir_exists(dir_path):
    """Creates directory if it not exists"""
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)


def execute_proc(cmd_name, source, dest):
    """Executes one of the preconfigured commands
    with {source} and {dest} parameters replacement"""
    cmd = conf[cmd_name].format(source=source, dest=dest)
    execute(cmd)


def execute(cmd, critical=False):
    """Execute system command"""
    try:
        log.debug("executing '%s'" % cmd)
        os.system(cmd)
    except:
        log.error('error executing system command')
        if critical:
            raise
        else:
            log.debug(traceback.format_exc())


def execute_after(cmd, delay):
    """This function intended to execute system command asyncronously"""
    time.sleep(delay)
    execute(cmd, True)


def check_build_is_done(build_path):
    """Check if the web content was built and exit if it isn't"""
    if not os.path.isdir(build_path):
        raise Exception("web content directory not exists: '%s'" % build_path)


def drop_build_dir(build_path, create_new=False):
    """Drops the build if it exists"""
    if os.path.isdir(build_path):
        shutil.rmtree(build_path, ignore_errors=True)
    if create_new and not os.path.isdir(build_path):
        os.makedirs(build_path)


def get_md_h1(text):
    """Extracts the first h1-header from markdown text"""
    matches = H1_PATTERN.search(text)
    return matches.group(1) if matches else ''


def purify_time(page, time_parm, default):
    """Returns time value from page dict. If there is no
    specified value, default will be returned."""
    if time_parm in page:
        page[time_parm] = time.strptime(page[time_parm], TIME_FMT)
    else:
        page[time_parm] = datetime.fromtimestamp(default)


def get_conf_path(conf_file, path):
    """Expands relative pathes using configuration file
    location as base directory. Absolute pathes will be
    returned as is."""
    if os.path.isabs(path):
        return path
    base_path = os.path.dirname(os.path.abspath(conf_file))
    return os.path.join(base_path, path)


def md(text):
    """Converts markdown formatted text to HTML"""
    try:
        # New Markdown instanse works faster on large amounts of text
        # than reused one (for some reason)
        mkdn = markdown.Markdown(extensions=conf['markdown_extensions'])
    except:
        log.error('markdown initialization error: probably bad extension names')
        raise

    try:
        return mkdn.convert(text.strip())
    except:
        log.error('markdown processing error')
        raise


def update_humans(source_file, dest_file):
    """Updates 'Last update' field in humans.txt file and saves the result
    to specified location.

    Arguments:
        source_file -- original humans.txt file. See http://humanstxt.org
            for the format details.
        dest_file -- location to save updated humans.txt. File name should
            be included."""

    try:
        with codecs.open(source_file, mode='r', encoding='utf8') as f:
            text = f.read()
        repl = r"\1 " + time.strftime("%Y/%m/%d", time.gmtime())
        text = re.sub(r"^(\s*Last\s+update\s*\:).*", repl, text,
                      flags=RE_FLAGS, count=1)
        with codecs.open(dest_file, mode='w', encoding='utf8') as f:
            f.write(text)
    except:
        message = "humans.txt processing failed ('%s' to '%s')"
        log.error(message % (source_file, dest_file))
        raise


def spawn_generic(path):
    """Clones generic site to specified directory"""
    generic_path = os.path.dirname(os.path.abspath(__file__))
    generic_path = os.path.join(generic_path, GENERIC_PATH)
    cp(generic_path, path)


def cp(src, dest):
    """Copies everything to anywhere"""
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            raise


# Command line command ========================================================

# Common arguments

path_arg = arg('path', default=None,
    help='path to the website to build (default is current directory)')

log_arg = arg('-l', '--log', default=None,
    help='log file name')

verbose_arg = arg('-v', '--verbose', default=False,
    help='enable verbose output')


@path_arg
@log_arg
@verbose_arg
def init(args):
    """create new website"""
    setup(args)
    log.info('new site created successfully, have fun!')


@path_arg
@log_arg
@verbose_arg
def build(args):
    """generate web content from source"""
    setup(args)
    drop_build_dir(conf['build_path'])
    ensure_dir_exists(conf['build_path'])
    log.info("building path: '%s'" % conf['build_path'])
    process_files()
    log.info("build succeeded")


@path_arg
@arg('-p', '--port', default=None, help='port for local HTTP server')
@arg('-b', '--browse', default=False, help='open in default browser')
@log_arg
@verbose_arg
def run(args):
    """run local web server to preview generated website"""
    setup(args)
    check_build_is_done(conf['build_path'])
    original_cwd = os.getcwd()
    port = str2int(args.port, conf['port'])
    log.info("running HTTP server on port %d..." % port)

    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from SocketServer import TCPServer
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(('', port), handler)

    try:
        if args.browse:
            url = "http://localhost:%s/" % port
            cmd = conf['run_browser_cmd'].format(url=url)
            delay = conf['browser_opening_delay']

            log.info("opening browser in %g seconds" % delay)
            log.info('use Ctrl-Break to stop webserver')
            log.debug("command: '%s'" % cmd)
            p = Process(target=execute_after, args=(cmd, delay))
            p.start()

        os.chdir(conf['build_path'])
        httpd.serve_forever()

    except KeyboardInterrupt:
        log.info('server was stopped by user')
    finally:
        os.chdir(original_cwd)


@path_arg
@log_arg
@verbose_arg
def deploy(args):
    """deploy generated website to the remote web server"""
    setup(args)
    check_build_is_done(conf['build_path'])

    if not conf['sync_cmd']:
        raise Exception('synchronizing command is not defined by configuration')

    log.info('synchronizing...')
    execute(conf['sync_cmd'].format(path=conf['build_path']), True)
    log.info('done')


@path_arg
@log_arg
@verbose_arg
def clean(args):
    """delete all generated content"""
    setup(args)
    log.info('cleaning output...')
    drop_build_dir(conf['build_path'])
    log.info('done')


@path_arg
@arg('-e', '--edit', default=False, help='open with preconfigured editor')
@log_arg
@verbose_arg
def page(args):
    setup(args)
    # TODO: ...
    if args.edit:
        print(os.path.expandvars(conf['editor_cmd']))


def main():  # For setuptools
    # Adding default value for 'path' positional argument
    commands = ['init', 'build', 'run', 'deploy', 'clean']
    if len(sys.argv) == 2 and sys.argv[1] in commands:
        sys.argv.append('.')

    p = ArghParser()
    p.add_commands([init, build, run, deploy, clean, page])
    p.dispatch()
    # try:
    #     p = ArghParser()
    #     p.add_commands([init, build, run, deploy, clean])
    #     p.dispatch()
    # except:
    #     l = log if len(log.handlers) else logging
    #     l.debug(traceback.format_exc())

if __name__ == '__main__':
    main()

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

import authoring
import markdown
import pystache
import yaml

__author__ = authoring.AUTHOR
__email__ = authoring.EMAIL
__copyright__ = authoring.COPYRIGHT
__license__ = authoring.LICENSE
__version_info__ = authoring.VERSION_INFO
__version__ = authoring.VERSION
__status__ = authoring.STATUS
__url__ = authoring.URL

NAME = os.path.splitext(os.path.basename(__file__))[0]
DEFAULT_LOG = 'pub.log'
DEFAULT_CONF = 'pub.conf'
GENERIC_PATH = 'generic-site'
GENERIC_PAGES = 'generic-pages'

# See the docs for parameters description
CONF = {
    'generator': NAME + " {version}",
    'build_path': 'www',
    'pages_path': 'pages',
    'static_path': 'static',
    'templates_path': 'templates',
    'port': 8000,
    'browser_opening_delay': 2.0,
    'template': 'default',
    'author': '',
    'minify_js': True,
    'minify_css': True,
    'minify_less': True,
    'minify_js_cmd': "yuicompressor --type js --nomunge -o {dest} {source}",
    'minify_css_cmd': "yuicompressor --type css -o {dest} {source}",
    'sync_cmd': '',
    'run_browser_cmd': "start {url}",
    'less_cmd': "lessc -x {source} > {dest}",
    'markdown_extensions': ['nl2br', 'grid', 'smartypants'],
    'editor_cmd': "$EDITOR \"{source}\"",
    'conf': '',
}

LOG_CONSOLE_FMT = ("%(asctime)s %(levelname)s: %(message)s", "%H:%M:%S")
LOG_FILE_FMT = ("%(asctime)s %(levelname)s: %(message)s", "%Y/%m/%d %H:%M:%S")
TIME_FMT = "%Y/%m/%d %H:%M:%S"
RE_FLAGS = re.I | re.M | re.U
PARAM_PATTERN = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", RE_FLAGS)
H1_PATTERN = re.compile(r"^\s*#\s*(.*)\s*", RE_FLAGS)
POST_PATTERN = re.compile(r"[\w\\/]+")
URI_SEP_PATTERN = re.compile(r"[^a-z\d]+", RE_FLAGS)
URI_EXCLUDE_PATTERN = re.compile(r"[,.`\'\"\!@\#\$\%\^\&\*\(\)\+]+", RE_FLAGS)

log = logging.getLogger(__name__)
conf = {}


# Initialization =============================================================

def setup(args):
    """Initializes website configuration from command line arguments. Creates
    new site directory if init is True, or reads specified configuration file
    otherwise."""
    config = args.source or '.'
    config = os.path.abspath(os.path.join(config, DEFAULT_CONF))
    init_logging(args.log, args.verbose)

    global conf

    if args.function == init:
        try:
            site_path = os.path.dirname(config)
            if os.path.isdir(site_path):
                log.error("directory already exists: '%s'" % site_path)
                exit()

            log.info("creating new website at '%s'" % site_path)
            spawn(site_path)

            text = yaml.dump(CONF, width=80, indent=4, default_flow_style=False)
            with codecs.open(config, mode='w', encoding='utf8') as f:
                f.write(text)
            conf = purify_conf(CONF)
        except:
            log.error('initialization failed')
            raise
    else:
        try:
            log.debug("loading website configuration from '%s'" % config)
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
            makedirs(os.path.dirname(log_file))
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
        makedirs(dest_path)

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
        page = read_page(source_file)
        with codecs.open(dest_file, mode='w', encoding='utf8') as f:
            tpl = get_template(page['template'], templates_path)
            f.write(pystache.render(tpl, page))
    except Exception as e:
        log.debug(traceback.format_exc())
        log.error('content processing error: ' + str(e))


def read_page(source_file):
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

        page['title'] = page.get('title', get_h1(page['content'])).strip()
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
            to file name using '.mustache').
        templates_path -- template files path."""
    file_name = os.path.join(templates_path, tpl_name + '.mustache')
    if os.path.exists(file_name):
        with codecs.open(file_name, mode='r', encoding='utf8') as f:
            return f.read()

    raise Exception("template not exists: '%s'" % file_name)


# General helpers =============================================================

def str2int(value, default=None):
    """Safely converts string value to integer. Returns
    default value if the first argument is not numeric.
    Whitespaces are ok."""
    if type(value) is not int:
        value = str(value).strip()
        value = int(value) if value.isdigit() else default
    return value


def makedirs(dir_path):
    """Creates directory if it not exists"""
    if dir_path and not os.path.exists(dir_path):
        log.debug("creating directory '%s'" % dir_path)
        os.makedirs(dir_path)


def execute_proc(cmd_name, source, dest=None):
    """Executes one of the preconfigured commands
    with {source} and {dest} parameters replacement"""
    if dest:
        cmd = conf[cmd_name].format(source=source, dest=dest)
    else:
        cmd = conf[cmd_name].format(source=source)
    execute(os.path.expandvars(cmd))


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


def check_build(path):
    """Check if the web content was built and exit if it isn't"""
    if not os.path.isdir(path):
        raise Exception("web content directory not exists: '%s'" % path)


def drop_build(path, create=False):
    """Drops the build if it exists"""
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    if create and not os.path.isdir(path):
        os.makedirs(path)


def get_h1(text):
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


def spawn(path):
    """Clones generic site to specified directory"""
    generic = os.path.dirname(os.path.abspath(__file__))
    generic = os.path.join(generic, GENERIC_PATH)
    cp(generic, path)


def get_generic(name):
    """Returns full path to specified generic page"""
    try:
        generic = os.path.dirname(os.path.abspath(__file__))
        generic = os.path.join(generic, GENERIC_PAGES)
        generic = os.path.join(generic, str(name) + '.md')
        with codecs.open(generic, mode='r', encoding='utf8') as f:
            return f.read()
    except:
        log.error("error reading generic post: '%s'" % str(name))
        raise


def cp(src, dest):
    """Copies everything to anywhere"""
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            raise


def get_log():
    return log if len(log.handlers) else logging


def yml(data, file_name):
    text = yaml.dump(data, width=80, indent=4, default_flow_style=False)
    with codecs.open(file_name, mode='w', encoding='utf8') as f:
        f.write(text)


def unyml(file_name):
    with codecs.open(file_name, mode='r', encoding='utf8') as f:
        return yaml.load(f.read())


def create_feed(path):

    # try:
        # from pprint import pprint
        loaded = unyml(conf['conf'])

        if not 'feeds' in loaded:
            loaded['feeds'] = []

        if not path in loaded['feeds']:
            loaded['feeds'].append(path)
            bak = conf['conf'] + '.old'
            if os.path.exists(bak):
                os.remove(bak)
            yml(loaded, conf['conf'])

        exit()

    # except:
    #     log.error('error adding feed info to site configuration')
    #     raise
    # """Create marker file at the specified folder to inform the
    # site builder it contains blog structure"""
    # try:
    #     feed_marker = os.path.join(path, FEED_MARKER)
    #     if not os.path.exists(feed_marker):
    #         log.debug("creating feed marker: '%s'" % feed_marker)
    #         open(feed_marker, 'w').close()
    #         # TODO: Write default cfg
    #         # with codecs.open(feed_marker, mode='w', encoding='utf8') as f:
    #         #     f.write('')
    # except:
    #     log.error('error checking/creating feed marker')
    #     raise


def urlify(string):
    """Make a string URL-safe by excluding unwanted characters
    and replacing spaces with dashes. Used to generate URIs from
    post titles.

    Usage:

        >>> urlify("Hello World")
        "hello-world"
        >>> urlify("Drugs, Sex and Rock'n'Roll!")
        "drugs-sex-and-rocknroll"
    """
    result = URI_EXCLUDE_PATTERN.sub('', string)
    result = URI_SEP_PATTERN.sub('-', result)
    return result.strip('-').lower()


def create_page(name, date, text, force):
    """Creates page file"""
    name = urlify(name)
    page_path = os.path.join(conf['pages_path'], name) + '.md'

    if os.path.exists(page_path):
        if force:
            log.debug('existing page will be overwritten')
        else:
            raise Exception('page already exists, use -f to overwrite')

    text = text.format(title=name, ctime=date.strftime(TIME_FMT))
    makedirs(os.path.split(page_path)[0])

    with codecs.open(page_path, mode='w', encoding='utf8') as f:
        log.debug("creating page '%s'" % page_path)
        f.write(text)


def create_post(name, date, text):
    """Generates post file placeholder with an unique name
    and returns its name"""
    feed_name, post_name = os.path.split(name)

    # TODO: Use the Force

    # Create new feed if not exists
    feed_path = os.path.join(conf['pages_path'], feed_name)
    create_feed(feed_name)
    feed_path = os.path.join(feed_path, date.strftime('%Y'))
    makedirs(feed_path)

    # Generate new post file name
    parts = [date.strftime('%Y-%m-%d'), urlify(post_name)]
    post_name = '_'.join(filter(None, parts)) + '.md'
    new_name = os.path.join(feed_path, post_name)
    text = text.format(title=name, ctime=date.strftime(TIME_FMT))
    num = 1

    # Preserve file with a new unique name
    while True:
        if not os.path.exists(new_name):
            log.debug("creating post '%s'" % new_name)
            with codecs.open(new_name, mode='w', encoding='utf8') as f:
                f.write(text)
            return new_name

        num += 1
        base, ext = os.path.splitext(post_name)
        new_name = os.path.join(feed_path, base) + str(num) + ext


# Command line command ========================================================

# Common arguments

source_arg = arg('-s', '--source', default=None, metavar='SRC',
    help='website source path (default is the current directory)')

log_arg = arg('-l', '--log', default=None,
    help='log file name')

verbose_arg = arg('-v', '--verbose', default=False,
    help='verbose output')

force_arg = arg('-f', '--force', default=False,
    help='overwrite existing files')

type_arg = arg('-t', '--type', default=None,
    help='generic page to clone')

edit_arg = arg('-e', '--edit', default=False,
    help='open with preconfigured editor')


@source_arg
@log_arg
@verbose_arg
def init(args):
    """create new website"""
    setup(args)
    log.info('new site created successfully, have fun!')


@source_arg
@log_arg
@verbose_arg
def build(args):
    """generate web content from source"""
    setup(args)
    drop_build(conf['build_path'])
    makedirs(conf['build_path'])
    log.info("building path: '%s'" % conf['build_path'])
    process_files()
    log.info("build succeeded")

    # TODO: Build feeds
    # rebuild index - text file: path->title
    # update archive page
    # update rss
    # update atom


@source_arg
@arg('-p', '--port', default=None, help='port for local HTTP server')
@arg('-b', '--browse', default=False, help='open in default browser')
@log_arg
@verbose_arg
def run(args):
    """run local web server to preview generated website"""
    setup(args)
    check_build(conf['build_path'])
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


@source_arg
@log_arg
@verbose_arg
def deploy(args):
    """deploy generated website to the remote web server"""
    setup(args)
    check_build(conf['build_path'])

    if not conf['sync_cmd']:
        raise Exception('synchronizing command is not defined by configuration')

    log.info('synchronizing...')
    execute(conf['sync_cmd'].format(path=conf['build_path']), True)
    log.info('done')


@source_arg
@log_arg
@verbose_arg
def clean(args):
    """delete all generated content"""
    setup(args)
    log.info('cleaning output...')
    drop_build(conf['build_path'])
    log.info('done')


@arg('name', help='page name (may include path)')
@source_arg
@force_arg
@edit_arg
@type_arg
@log_arg
@verbose_arg
def page(args):
    """create new page"""

    # Test:
    # python publicstatic/publicstatic.py page -s test-site2 -v one

    setup(args)
    if not POST_PATTERN.match(args.name):
        raise Exception('illegal page name')

    text = get_generic(args.type or 'default-page')
    page_path = create_page(args.name, datetime.now(), text, args.force)

    if args.edit:
        execute_proc('editor_cmd', page_path)


@arg('name', help='post name and optional feed name')
@source_arg
@edit_arg
@type_arg
@log_arg
@verbose_arg
def post(args):
    """create new post"""

    # Test:
    # python publicstatic/publicstatic.py post -s test-site2 -v "blog\hello world"

    setup(args)

    if not POST_PATTERN.match(args.name):
        raise Exception('illegal feed or post name')

    text = get_generic(args.type or 'default-post')
    post_path = create_post(args.name, datetime.now(), text)

    if args.edit:
        execute_proc('editor_cmd', post_path)


def main():
    try:
        p = ArghParser()
        p.add_commands([init, build, run, deploy, clean, page, post])
        p.dispatch()
        return 0
    except KeyboardInterrupt:
        get_log().info('killed by user')
        return 1
    except Exception as e:
        get_log().error(str(e))
        get_log().debug(traceback.format_exc())
        return 2

if __name__ == '__main__':
    sys.exit(main())

# coding: utf-8

"""public-static - static website builder"""

import codecs
from datetime import datetime
from multiprocessing import Process
import os
import re
import shutil
import sys
import traceback
from argh import ArghParser, arg
import jinja2
from . import conf
from . import constants
from . import logger
from . import tools
from .lib.pyatom import AtomFeed
from .version import get_version

_tplenv = None


def _init(conf_path, verbose=False, use_defaults=False):
    """Init configuration and logger"""
    conf.init(conf_path, use_defaults)
    logger.init(verbose=verbose)


def _exec(command, source, dest=''):
    """Safely executes one of the preconfigured commands
    with {source} and {dest} parameter replacements"""
    cmd = os.path.expandvars(command.format(source=source, dest=dest))
    logger.debug("executing '%s'" % cmd)
    try:
        os.system(cmd)
    except:
        logger.error('error executing system command')
        logger.debug(traceback.format_exc())


# Website building

def process_dir(path):
    """Process a directory containing independent
    files like website pages or assets."""
    logger.debug("source path: '%s'" % path)
    tools.walk(path, process_file)


def process_file(root_dir, rel_source):
    """Process single web page source file or static asset.

    Arguments:
        root_dir -- root files directory (e.g. 'pages').
        rel_source -- source file relative path."""

    source_file = os.path.join(root_dir, rel_source)
    ext = os.path.splitext(rel_source)[1]
    dest_file = tools.dest(conf.get('build_path'), rel_source)
    tools.makedirs(os.path.dirname(dest_file))

    if ext == '.md':
        logger.info("- %s => %s" % (rel_source,
            os.path.relpath(dest_file, conf.get('build_path'))))
        build_page(parse(source_file), dest_file)

    elif ext == '.less':
        logger.info('compiling LESS: ' + rel_source)
        if conf.get('min_less'):
            tmp_file = dest_file + '.tmp'
            _exec(conf.get('less_cmd'), source_file, tmp_file)
            _exec(conf.get('min_css_cmd'), tmp_file, dest_file)
            os.remove(tmp_file)
        else:
            _exec(conf.get('less_cmd'), source_file, dest_file)

    elif ext == '.css' and conf.get('min_css') and conf.get('min_css_cmd'):
        logger.info('minifying CSS: ' + rel_source)
        _exec(conf.get('min_css_cmd'), source_file, dest_file)

    elif ext == '.js' and conf.get('min_js') and conf.get('min_js_cmd'):
        logger.info('minifying JS: ' + rel_source)
        _exec(conf.get('min_js_cmd'), source_file, dest_file)

    elif os.path.basename(source_file) == 'humans.txt':
        logger.info('copying: %s (updated)' % rel_source)
        tools.update_humans(source_file, dest_file)

    else:
        logger.info('copying: ' + rel_source)
        shutil.copyfile(source_file, dest_file)


def process_blog(path):
    """Generate blog post pages"""
    posts = tools.posts(path)
    prev = None
    next = None
    index = []

    # Put the latest post at site root URL if True
    root_post = conf.get('post_at_root_url')
    build_path = conf.get('build_path')

    for i in range(len(posts)):
        source_file, ctime = posts[i]
        data = next or parse(os.path.join(path, source_file), is_post=True)
        if i + 1 < len(posts):
            next = parse(os.path.join(path, posts[i + 1][0]), is_post=True)
        else:
            next = None

        dest_file = tools.post_path(source_file, ctime)
        logger.info("- %s => %s" % (posts[i][0], dest_file))
        dest_file = os.path.join(build_path, dest_file)
        tools.makedirs(os.path.dirname(dest_file))

        data['prev_url'] = tools.post_url(prev)
        data['prev_title'] = prev and prev['title']
        data['next_url'] = tools.post_url(next)
        data['next_title'] = next and next['title']

        index.append(tools.feed_data(data))
        build_page(data, dest_file)

        if next == None and root_post:
            # Generate a copy for the latest post in the site root
            dest_file = os.path.join(build_path, conf.get('index_page'))
            if os.path.exists(dest_file):
                logger.warn('index page will be overwritten by latest post')
            build_page(data, dest_file)

        prev = data

    logger.info('building blog index...')
    build_indexes(index[::-1])

    logger.info('building atom feed...')
    build_feed(index)


def build_page(data, dest_file):
    """Builds a web page

    Arguments:
        data -- page data dict.
        dest_file -- full path to the destination file."""

    common_data = {
        'root_url': conf.get('root_url'),
        'rel_root_url': conf.get('rel_root_url'),
        'archive_url': conf.get('rel_root_url') + conf.get('archive_page'),
        'site_title': conf.get('title'),
        'site_subtitle': conf.get('subtitle'),
        'menu': conf.get('menu'),
    }
    common_data.update(data)
    try:
        tpl = get_tpl(data['template'])
        with codecs.open(dest_file, mode='w', encoding='utf8') as f:
            f.write(tpl.render(common_data))
    except jinja2.TemplateSyntaxError as e:
        message = 'template syntax error: %s (file: %s; line: %d)'
        logger.error(message % (e.message, e.filename, e.lineno))
        raise
    except jinja2.TemplateNotFound as e:
        message = "template not found: '%s' at '%s'"
        logger.error(message % (e.name, conf.get('tpl_path')))
        raise
    except Exception as e:
        logger.error('page building error: ' + str(e))
        logger.debug(traceback.format_exc())


def build_feed(data):
    """Builds atom feed for the blog"""
    feed_url = conf.get('root_url') + conf.get('atom_feed')
    feed = AtomFeed(title=conf.get('title'),
                    subtitle=conf.get('subtitle'),
                    feed_url=feed_url,
                    url=conf.get('root_url'),
                    author=conf.get('author'))

    for item in data:
        feed.add(title=item['title'],
                 content=item['content'],
                 content_type='html',
                 author=item['author'],
                 url=item['full_url'],
                 updated=item['updateddt'])

    try:
        feed_file = tools.dest(conf.get('build_path'), conf.get('atom_feed'))
        with codecs.open(feed_file, mode='w', encoding='utf8') as f:
            f.write(feed.to_string())
    except:
        logger.error("error writing atom feed to '%s'" % feed_file)
        raise


def build_indexes(data):
    """Build post list pages"""
    index_data = {
        'title': conf.get('archive_page_title'),
        'author': conf.get('author'),
        'generator': constants.GENERATOR.format(version=get_version()),
        'template': 'archive',
        'posts_num': len(data),
        'posts': data,
    }
    dest_file = os.path.join(conf.get('build_path'), conf.get('archive_page'))
    build_page(index_data, dest_file)


def parse(source_file, is_post=False):
    """Reads a post/page file to dictionary.

    Arguments:
        source_files -- path to the source file.
        is_post -- source file is a blog post.
        header -- returns {file_name, created, and title} only."""

    data = {}
    with codecs.open(source_file, mode='r', encoding='utf8') as f:
        # Extract page metadata if header lines presents
        lines = f.readlines()
        for num, line in enumerate(lines):
            parsed = tools.parse_param(line)
            if parsed:
                data[parsed[0]] = parsed[1]
            else:
                data['content'] = ''.join(lines[num:])
                break

    data['source'] = source_file
    data['title'] = data.get('title', tools.get_h1(data['content']))

    deftpl = conf.get('post_tpl' if is_post else 'page_tpl')
    data['template'] = data.get('template', deftpl).strip()

    data['author'] = data.get('author', conf.get('author')).strip()

    extensions = conf.get('markdown_extensions')
    data['content'] = tools.md(data.get('content', ''), extensions)

    tags = list(map(str.strip, filter(None, data.get('tags', '').split(','))))
    tags = tags or conf.get('default_tags')
    data['tags'] = [ { 'name': tag, 'url': tools.tag_url(tag) } for tag in tags ]

    def purify_time(param, get_time):
        if param in data:
            value = tools.parse_time(data[param])
        else:
            value = get_time(source_file)
        data[param] = datetime.fromtimestamp(value)

    purify_time('created', os.path.getctime)
    purify_time('updated', os.path.getmtime)

    return data


def get_tpl(tpl_name):
    """Gets template file contents.

    Arguments:
        tpl_name -- template name (will be complemented
            to file name using '.mustache')."""

    global _tplenv
    if _tplenv is None:
        loader = jinja2.FileSystemLoader(searchpath=conf.get('tpl_path'))
        _tplenv = jinja2.Environment(loader=loader)

    file_name = tpl_name + '.html'
    return _tplenv.get_template(file_name)


def create_page(name, text, date, force):
    """Creates page file

    Arguments:
        name -- page name (will be used for file name and URL).
        text -- page text.
        date -- creation date and time (struct_time).
        force -- True to overwrite existing file; False to throw exception."""

    name = tools.urlify(name)
    logger.debug("creating page '%s'" % name)
    page_path = os.path.join(conf.get('pages_path'), name) + '.md'

    if os.path.exists(page_path):
        if force:
            logger.debug('existing page will be overwritten')
        else:
            logger.error('page already exists, use -f to overwrite')
            return None

    text = text.format(title=name, created=date.strftime(constants.TIME_FMT))
    tools.makedirs(os.path.split(page_path)[0])

    with codecs.open(page_path, mode='w', encoding='utf8') as f:
        f.write(text)
    return page_path


def create_post(name, text, date, force):
    """Generates post file placeholder with an unique name
    and returns its name

    Arguments:
        name -- post name (will be used for file name and URL).
        text -- post text.
        date -- creation date and time (struct_time).
        force -- True to overwrite existing file; False to throw exception."""

    post_name = '%s-%s{suffix}.md' % (date.strftime('%Y%m%d'), tools.urlify(name))
    post_path = os.path.join(conf.get('posts_path'), post_name)
    tools.makedirs(os.path.dirname(post_path))

    # Generate new post file name and preserve file with a new unique name
    num = 1
    while True:
        result = post_path.format(suffix=str(num) if num > 1 else '')
        if force or not os.path.exists(result):
            logger.debug("creating post '%s'" % result)
            text = text.format(title=name,
                               created=date.strftime(constants.TIME_FMT))
            with codecs.open(result, mode='w', encoding='utf8') as f:
                f.write(text)
            return result
        else:
            num += 1


# Common command line arguments

source_arg = arg('-s','--source', default=None, metavar='SRC',
                 help='website source path (default is the current directory)')

log_arg = arg('-l','--log', default=None,
              help='log file name')

verbose_arg = arg('-v', '--verbose', default=False,
                  help='verbose output')

force_arg = arg('-f', '--force', default=False,
                help='overwrite existing files')

type_arg = arg('-t', '--type', default=None,
               help='generic page to clone')

edit_arg = arg('-e', '--edit', default=False,
               help='open with preconfigured editor')


# Commands

@source_arg
@log_arg
@verbose_arg
def init(args):
    """create new website"""
    _init(args.source, args.verbose, True)

    try:
        site_path = os.path.dirname(conf.get_path())
        if os.path.isdir(site_path):
            logger.warn("directory already exists: '%s'" % site_path)
        tools.spawn_site(site_path)
        conf.write_defaults()
        logger.info('website created successfully, have fun!')
    except:
        logger.error('initialization failed')
        raise


@source_arg
@log_arg
@verbose_arg
def build(args):
    """generate web content from source"""
    _init(args.source, args.verbose)
    tools.drop_build(conf.get('build_path'))
    tools.makedirs(conf.get('build_path'))
    logger.info("building path: '%s'" % conf.get('build_path'))
    logger.info('processing assets...')
    process_dir(conf.get('assets_path'))
    logger.info('processing blog posts...')
    process_blog(conf.get('posts_path'))
    logger.info('processing pages...')
    process_dir(conf.get('pages_path'))
    logger.info('done')


@source_arg
@arg('-p', '--port', default=None, help='port for local HTTP server')
@arg('-b', '--browse', default=False, help='open in default browser')
@log_arg
@verbose_arg
def run(args):
    """run local web server to preview generated website"""
    _init(args.source, args.verbose)
    tools.check_build(conf.get('build_path'))
    original_cwd = os.getcwd()
    port = tools.str2int(args.port, conf.get('port'))
    logger.info("running HTTP server on port %d..." % port)

    from http.server import SimpleHTTPRequestHandler
    from socketserver import TCPServer
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(('', port), handler)

    try:
        if args.browse:
            url = "http://localhost:%s/" % port
            delay = conf.get('browser_delay')
            logger.info("opening browser in %g seconds" % delay)
            p = Process(target=tools.browse, args=(url, delay))
            p.start()

        logger.info('use Ctrl-Break to stop webserver')
        os.chdir(conf.get('build_path'))
        httpd.serve_forever()

    except KeyboardInterrupt:
        logger.info('server was stopped by user')
    finally:
        os.chdir(original_cwd)


@source_arg
@log_arg
@verbose_arg
def deploy(args):
    """deploy generated website to the remote web server"""
    _init(args.source, args.verbose)
    tools.check_build(conf.get('build_path'))

    if not conf.get('deploy_cmd'):
        raise Exception('deploy command is not defined')

    logger.info('deploying website...')
    cmd = conf.get('deploy_cmd').format(build_path=conf.get('build_path'))

    from subprocess import call
    call(cmd)

    logger.info('done')


@source_arg
@log_arg
@verbose_arg
def clean(args):
    """delete all generated content"""
    _init(args.source, args.verbose)
    logger.info('cleaning output...')
    tools.drop_build(conf.get('build_path'))
    logger.info('done')


@arg('name', help='page name (may include path)')
@source_arg
@force_arg
@edit_arg
@type_arg
@log_arg
@verbose_arg
def page(args):
    """create new page"""
    _init(args.source, args.verbose)
    if not tools.valid_name(args.name):
        raise Exception('illegal page name')

    text = tools.prototype(args.type or 'default-page')
    page_path = create_page(args.name, text, datetime.now(), args.force)

    if not page_path:
        return

    logger.info('page cerated')
    if args.edit:
        _exec(conf.get('editor_cmd'), page_path)


@arg('name', help='post name and optional feed name')
@source_arg
@force_arg
@edit_arg
@type_arg
@log_arg
@verbose_arg
def post(args):
    """create new post"""
    _init(args.source, args.verbose)
    if not tools.valid_name(args.name):
        raise Exception('illegal feed or post name')

    text = tools.prototype(args.type or 'default-post')
    try:
        post_path = create_post(args.name, text, datetime.now(), args.force)
    except:
        logger.error('error creating new post')
        raise

    logger.info('post cerated')

    if args.edit:
        _exec(conf.get('editor_cmd'), post_path)


def version(args):
    """show version"""
    return get_version()


def main():
    try:
        p = ArghParser()
        p.add_commands([init, build, run, deploy, clean, page, post, version])
        p.dispatch()
        return 0

    except Exception as e:
        import logging
        logging.basicConfig()
        logging.error(str(e))
        logging.debug(traceback.format_exc())
        return 2

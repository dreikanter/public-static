# coding: utf-8

"""Website building routines."""

import codecs
from datetime import datetime
import os
import shutil
import traceback
from publicstatic import conf
from publicstatic import const
from publicstatic import logger
from publicstatic import helpers
from publicstatic import templates
from publicstatic.lib.pyatom import AtomFeed
from publicstatic.urlify import urlify
from publicstatic.version import get_version


def process_dir(path):
    """Process a directory containing independent
    files like website pages or assets."""

    logger.debug("source path: '%s'" % path)
    helpers.walk(path, process_file)


def process_file(root_dir, rel_source):
    """Process single web page source file or static asset.

    Arguments:
        root_dir -- root files directory (e.g. 'pages').
        rel_source -- source file relative path."""

    source_file = os.path.join(root_dir, rel_source)
    ext = os.path.splitext(rel_source)[1]
    dest_file = helpers.dest(conf.get('build_path'), rel_source)
    helpers.makedirs(os.path.dirname(dest_file))

    if ext == '.md':
        logger.info("- %s => %s" % (rel_source,
            os.path.relpath(dest_file, conf.get('build_path'))))
        build_page(parse(source_file), dest_file)

    elif ext == '.less':
        logger.info('compiling LESS: ' + rel_source)
        if conf.get('min_css'):
            tmp_file = dest_file + '.tmp'
            helpers.execute(conf.get('less_cmd'), source_file, tmp_file)
            helpers.execute(conf.get('min_css_cmd'), tmp_file, dest_file)
            os.remove(tmp_file)
        else:
            helpers.execute(conf.get('less_cmd'), source_file, dest_file)

    elif ext == '.css' and conf.get('min_css') and conf.get('min_css_cmd'):
        logger.info('minifying CSS: ' + rel_source)
        helpers.execute(conf.get('min_css_cmd'), source_file, dest_file)

    elif ext == '.js' and conf.get('min_js') and conf.get('min_js_cmd'):
        logger.info('minifying JS: ' + rel_source)
        helpers.execute(conf.get('min_js_cmd'), source_file, dest_file)

    elif os.path.basename(source_file) == 'humans.txt':
        logger.info('copying: %s (updated)' % rel_source)
        helpers.update_humans(source_file, dest_file)

    else:
        logger.info('copying: ' + rel_source)
        shutil.copyfile(source_file, dest_file)


def process_blog(path):
    """Generate blog post pages."""

    posts = helpers.posts(path)
    prev = None
    next = None
    index = []

    # Put the latest post at site root URL if True
    root_post = conf.get('post_at_root_url')
    build_path = conf.get('build_path')

    for i in range(len(posts)):
        source_file, ctime = posts[i]
        source_file = os.path.join(path, source_file)
        data = next or parse(source_file, is_post=True)
        if i + 1 < len(posts):
            next = parse(os.path.join(path, posts[i + 1][0]), is_post=True)
        else:
            next = None

        dest_file = helpers.post_path(source_file, ctime)
        logger.info("- %s => %s" % (posts[i][0], dest_file))
        dest_file = os.path.join(build_path, dest_file)
        helpers.makedirs(os.path.dirname(dest_file))

        data['prev_url'] = helpers.post_url(prev)
        data['prev_title'] = prev and prev['title']
        data['next_url'] = helpers.post_url(next)
        data['next_title'] = next and next['title']
        data['permalink'] = helpers.post_url(data, full=True)

        index.append(helpers.feed_data(data))
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

    pagedata = get_commons()
    pagedata.update(data)

    try:
        templates.render(data, dest=dest_file)
    except Exception as ex:
        logger.error('page building error: ' + str(ex))
        logger.debug(traceback.format_exc())


def build_feed(data):
    """Builds atom feed for the blog."""

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
                 updated=item['updated'])

    try:
        feed_file = helpers.dest(conf.get('build_path'), conf.get('atom_feed'))
        with codecs.open(feed_file, mode='w', encoding='utf8') as f:
            f.write(feed.to_string())
    except:
        logger.error("error writing atom feed to '%s'" % feed_file)
        raise


def build_indexes(data):
    """Build post list pages."""

    index_data = {
        'author': conf.get('author'),
        'generator': const.GENERATOR,
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
            parsed = helpers.parse_param(line)
            if parsed:
                data[parsed[0]] = parsed[1]
            else:
                data['content'] = ''.join(lines[num:])
                break

    data['source'] = source_file
    data['title'] = data.get('title', helpers.get_h1(data['content']))

    deftpl = conf.get('post_tpl' if is_post else 'page_tpl')
    data['template'] = data.get('template', deftpl).strip()

    data['author'] = data.get('author', conf.get('author')).strip()

    extensions = conf.get('markdown_extensions')
    data['content'] = helpers.md(data.get('content', ''), extensions)

    tags = list(map(str.strip, filter(None, data.get('tags', '').split(','))))
    tags = tags or conf.get('default_tags')
    data['tags'] = [ { 'name': tag, 'url': helpers.tag_url(tag) } for tag in tags ]

    url = "{source_url}blob/master/{page_type}/{source_file}"
    data['source_url'] = url.format(source_url=conf.get('source_url'),
                                    page_type=('posts' if is_post else 'pages'),
                                    source_file=os.path.basename(source_file))


    def purifytime(field, getter):
        try:
            result = helpers.parse_time(data[field])
        except:
            result = datetime.fromtimestamp(getter(source_file))
        data[field] = result

    purifytime('created', os.path.getctime)
    purifytime('updated', os.path.getmtime)

    return data


def create_page(name, text, date, force):
    """Creates page file

    Arguments:
        name -- page name (will be used for file name and URL).
        text -- page text.
        date -- creation date and time (struct_time).
        force -- True to overwrite existing file; False to throw exception."""

    name = urlify(name)
    logger.debug("creating page '%s'" % name)
    page_path = os.path.join(conf.get('pages_path'), name) + '.md'

    if os.path.exists(page_path):
        if force:
            logger.debug('existing page will be overwritten')
        else:
            logger.error('page already exists, use -f to overwrite')
            return None

    timef = conf.get('time_format')[0]
    text = text.format(title=name, created=date.strftime(timef))
    helpers.makedirs(os.path.split(page_path)[0])

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

    logger.debug("urlify: %s -> %s" % (name, urlify(name)))
    post_name = '%s-%s{suffix}.md' % (date.strftime('%Y%m%d'), urlify(name))
    post_path = os.path.join(conf.get('posts_path'), post_name)
    helpers.makedirs(os.path.dirname(post_path))

    # Generate new post file name and preserve file with a new unique name
    num = 1
    while True:
        result = post_path.format(suffix=("-%d" % num) if num > 1 else '')
        if force or not os.path.exists(result):
            logger.debug("creating post '%s'" % result)
            timef = conf.get('time_format')[0]
            text = text.format(title=name, created=date.strftime(timef))
            with codecs.open(result, mode='w', encoding='utf8') as f:
                f.write(text)
            return result
        else:
            num += 1


def get_commons():
    """Returns comman data fields for page building."""

    return {
        'root_url': conf.get('root_url'),
        'rel_root_url': conf.get('rel_root_url'),
        'archive_url': conf.get('rel_root_url') + conf.get('archive_page'),
        'site_title': conf.get('title'),
        'site_subtitle': conf.get('subtitle'),
        'menu': conf.get('menu'),
        'time': datetime.now(),
        'author': conf.get('author'),
        'author_url': conf.get('author_url'),
        'generator': const.GENERATOR,
        'source_url': conf.get('source_url'),
        'enable_search_form': conf.get('enable_search_form'),
    }


# def _process(cache, ext, cmd, enabled, message):
#     for source in cache.assets(ext=ext):
#         helpers.makedirs(source.dest_dir())
#         command = conf.get(cmd)
#         if conf.get(enabled) and command:
#             logger.info("%s: %s" % (message, source.rel_path()))
#             helpers.execute(command, source.path(), source.dest())
#         else:
#             logger.info("%s: %s" % ('copying', source.rel_path()))
#             shutil.copyfile(source.path(), source.dest())


# def css(cache):
#     _process(cache, '.css', 'min_css_cmd', 'min_css', 'minifying CSS')


# def js(cache):
#     _process(cache, '.js', 'min_js_cmd', 'min_js', 'minifying JavaScript')


def css(cache):
    """Minify assets/*.css to {dest} (e.g. assets/styles/base.css
    will go to www/styles/base.css)."""
    for source in cache.assets(ext='.css'):
        helpers.makedirs(source.dest_dir())
        command = conf.get('min_css_cmd')
        if conf.get('min_css') and command:
            logger.info('minifying CSS: ' + source.rel_path())
            helpers.execute(command, source.path(), source.dest())
        else:
            logger.info('copying: ' + source.rel_path())
            shutil.copyfile(source.path(), source.dest())
        source.processed(True)


def js(cache):
    """Minify assets/*.js to {dest}."""
    for source in cache.assets(ext='.js'):
        helpers.makedirs(source.dest_dir())
        command = conf.get('min_js_cmd')
        if conf.get('min_js') and command:
            logger.info('minifying JavaScript: ' + source.rel_path())
            helpers.execute(command, source.path(), source.dest())
        else:
            logger.info('copying: ' + source.rel_path())
            shutil.copyfile(source.path(), source.dest())
        source.processed(True)


def less(cache):
    """Compile and minify assets/*.less to {dest}/*.css."""
    for source in cache.assets(ext='.less'):
        helpers.makedirs(source.dest_dir())
        logger.info('compiling LESS: ' + source.rel_path())
        if conf.get('min_css') and conf.get('min_css_cmd'):
            tmp_file = os.path.join(source.dest_dir(), '_' + source.basename())
            helpers.execute(conf.get('less_cmd'), source.path(), tmp_file)
            logger.info('minifying CSS: ' + source.rel_path())
            helpers.execute(conf.get('min_css_cmd'), tmp_file, source.dest())
            os.remove(tmp_file)
        else:
            helpers.execute(conf.get('less_cmd'), source.path(), source.dest())
        source.processed(True)


# def robots(cache):
#     """Build robots.txt."""
#     for source in cache.assets(basename='robots.txt'):
#         logger.info('processing ' + source.rel_path())
#         helpers.makedirs(source.dest_dir())
#         shutil.copyfile(source.path(), source.dest())
#         source.processed(True)


def humans(cache):
    """Build humans.txt."""
    for source in cache.assets(basename='humans.txt'):
        logger.info('processing ' + source.rel_path())
        try:
            templates.render(path=source.path(), dest=source.dest(), data={
                'author': conf.get('author'),
                'author_url': conf.get('author_url'),
                'author_twitter': conf.get('humans_author_twitter'),
                'author_location': conf.get('humans_author_location'),
                'last_updated': datetime.now(),
                'language': conf.get('humans_language'),
                'doctype': conf.get('humans_doctype'),
                'ide': conf.get('humans_ide'),
            })
        except Exception as ex:
            logger.error('humans.txt processing failed: ' + str(ex))
            logger.debug(traceback.format_exc())
        finally:
            source.processed(True)


def static(cache):
    """Copy other assets as is to the {dest}."""
    for source in cache.assets(processed=False):
        logger.info('copying: ' + source.rel_path())
        shutil.copyfile(source.path(), source.dest())
        source.processed(True)


def pages(cache):
    """Build pages/*.md to {dest} (independant, keep rel path)."""

    pass


def posts(cache):
    """Build posts/*.md to {dest}/{blog_path}; copy latest post to the root web page."""

    pass


def archive(cache):
    """Build blog archive page (full post list)."""

    pass


def tags(cache):
    """Build blog tag pages."""

    pass


def rss(cache):
    """Build rss feed."""

    pass


def atom(cache):
    """Build atom feed."""

    pass


def sitemap(cache):
    """Build sitemap.xml."""

    pass



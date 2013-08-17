# coding: utf-8

"""Website building routines."""

from datetime import datetime
import os
import shutil
import traceback
from publicstatic import conf
from publicstatic import logger
from publicstatic import helpers
from publicstatic import templates


def all():
    """Returns a sequence of builder functions."""
    return [
        css,
        js,
        less,
        robots,
        humans,
        static,
        pages,
        posts
    ]


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


def robots(cache):
    """Build robots.txt."""
    for source in cache.assets(basename='robots.txt'):
        logger.info('processing ' + source.rel_path())
        helpers.makedirs(source.dest_dir())
        try:
            templates.render(path=source.path(), dest=source.dest(), data={
                'tags_path': os.path.dirname(helpers.tag_url('')),
            })
        except Exception as ex:
            logger.error('robots.txt processing failed: ' + str(ex))
            logger.debug(traceback.format_exc())
        finally:
            source.processed(True)


def humans(cache):
    """Build humans.txt."""
    for source in cache.assets(basename='humans.txt'):
        logger.info('processing ' + source.rel_path())
        helpers.makedirs(source.dest_dir())
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
    for source in cache.pages():
        logger.info(_to('page', source.rel_path(), source.rel_dest()))
        helpers.makedirs(source.dest_dir())
        try:
            data = _complement(source.data(), cache)
            templates.render(data, dest=source.dest())
        except Exception as ex:
            logger.error('page building error: ' + str(ex))
            logger.debug(traceback.format_exc())


def posts(cache):
    """Build blog posts and copy the latest post to the site root."""
    for source in cache.posts():
        logger.info(_to('post', source.rel_path(), source.rel_dest()))
        helpers.makedirs(source.dest_dir())
        try:
            data = _complement(source.data())
            templates.render(data, dest=source.dest())
        except Exception as ex:
            logger.error('post building error: ' + str(ex))
            logger.debug(traceback.format_exc())

    if conf.get('post_at_root_url'):  # put the latest post at site root url
        last = cache.posts()[-1]
        path = os.path.join(conf.get('build_path'), conf.get('index_page'))
        logger.info(_to('root', last.rel_dest(), conf.get('index_page')))
        if any(cache.pages(dest=conf.get('index_page'))):
            logger.warn('root page will be overwritten by the latest post')
        shutil.copyfile(last.dest(), path)


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


def _complement(page_data, cache=None):
    """Complement individual page data with common variables and site index."""
    result = {
        'commons': conf.commons(),
        'page': page_data,
    }
    if cache:
        result['index'] = cache.data()
    return result


def _to(subj, src, dest):
    return "%s: %s -> %s" % (subj, src, dest)

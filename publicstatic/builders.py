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
        logger.info("page: %s -> %s" % (source.rel_path(), source.rel_dest()))
        helpers.makedirs(source.dest_dir())
        try:
            templates.render(source.data(), dest=source.dest())
        except Exception as ex:
            logger.error('page building error: ' + str(ex))
            logger.debug(traceback.format_exc())

def posts(cache):
    """Build blog posts and copy the latest post to the site root."""
    for source in cache.posts():
        logger.info("post: %s -> %s" % (source.rel_path(), source.rel_dest()))
        helpers.makedirs(source.dest_dir())
        try:
            templates.render(source.data(), dest=source.dest())
        except Exception as ex:
            logger.error('post building error: ' + str(ex))
            logger.debug(traceback.format_exc())

    # put the latest post at site root url
    if conf.get('post_at_root_url'):
        last = cache.posts()[-1]
        path = os.path.join(conf.get('build_path'), conf.get('index_page'))
        logger.info("root: %s -> %s" %
            (last.rel_dest(), conf.get('index_page')))
        if any(cache.pages(dest=conf.get('index_page'))):
            logger.warn('root page will be overwritten by the latest post')
        shutil.copyfile(last.dest(), path)


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

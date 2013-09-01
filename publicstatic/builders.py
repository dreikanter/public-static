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


def order():
    """Returns a sequence of builder functions."""
    return [
        css,
        js,
        less,
        robots,
        humans,
        static,
        pages,
        posts,
        archive,
        tags,
        atom,
        sitemap,
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
        helpers.utime(source.dest(), source.updated())
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
        helpers.utime(source.dest(), source.updated())
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
        helpers.utime(source.dest(), source.updated())
        source.processed(True)


def robots(cache):
    """Build robots.txt."""
    for source in cache.assets(basename='robots.txt'):
        logger.info('processing ' + source.rel_path())
        helpers.makedirs(source.dest_dir())
        try:
            data = {'tags_path': os.path.dirname(helpers.tag_url(''))}
            templates.render(data, source.dest(), path=source.path())
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
            data = {
                'author': conf.get('author'),
                'author_url': conf.get('author_url'),
                'author_twitter': conf.get('humans_author_twitter'),
                'author_location': conf.get('humans_author_location'),
                'last_updated': datetime.now(),
                'language': conf.get('humans_language'),
                'doctype': conf.get('humans_doctype'),
                'ide': conf.get('humans_ide'),
            }
            templates.render(data, source.dest(), path=source.path())
        except Exception as ex:
            logger.error('humans.txt processing failed: ' + str(ex))
            logger.debug(traceback.format_exc())
        finally:
            source.processed(True)


def static(cache):
    """Copy other assets as is to the {dest}."""
    for source in cache.assets(processed=False):
        logger.info('copying: ' + source.rel_path())
        helpers.makedirs(source.dest_dir())
        shutil.copyfile(source.path(), source.dest())
        helpers.utime(source.dest(), source.updated())
        source.processed(True)


def pages(cache):
    """Build pages/*.md to {dest} (independant, keep rel path)."""
    for source in cache.pages():
        logger.info(_to('page', source.rel_path(), source.rel_dest()))
        helpers.makedirs(source.dest_dir())
        try:
            data = _complement(source.data(), index=cache.index())
            templates.render(data, source.dest())
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
            templates.render(data, source.dest())
        except Exception as ex:
            logger.error('post building error: ' + str(ex))
            logger.debug(traceback.format_exc())

    if conf.get('post_at_root_url'):  # put the latest post at site root url
        last = cache.posts()[0]
        path = os.path.join(conf.get('build_path'), conf.get('index_page'))
        logger.info(_to('root', last.rel_dest(), conf.get('index_page')))
        if any(cache.pages(dest=conf.get('index_page'))):
            logger.warn('root page will be overwritten by the latest post')
        shutil.copyfile(last.dest(), path)
        helpers.utime(path, last.updated())


def archive(cache):
    dest = os.path.join(conf.get('build_path'), conf.get('archive_location'))
    logger.info('archive: ' + dest)
    helpers.makedirs(os.path.dirname(dest))
    data = _complement({'title': 'Archive'}, index=cache.index())
    templates.render(data, dest, name='archive.html')


def tags(cache):
    """Build blog tag pages."""
    for tag in cache.tags():
        dest = helpers.tag_path(tag)
        logger.info(_to('tag', tag, dest))
        helpers.makedirs(os.path.dirname(dest))
        data = _complement({'title': '#' + tag}, index=cache.index(tag=tag))
        templates.render(data, dest, name='tag.html')


def atom(cache):
    """Build atom feed."""
    data = _complement(index=cache.index())
    dest = os.path.join(conf.get('build_path'), conf.get('atom_location'))
    templates.render(data, dest, name='atom.xml')


def sitemap(cache):
    """Build sitemap.xml."""
    pass


def _complement(page_data=None, index=None):
    """Complement individual page data with common variables and site index."""
    return {
        'commons': conf.commons(),
        'page': page_data,
        'index': index if index is not None else [],
    }


def _to(subj, src, dest):
    return "%s: %s -> %s" % (subj, src, dest)

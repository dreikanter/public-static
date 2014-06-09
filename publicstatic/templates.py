# coding: utf-8

"""Jinja2 helpers."""

import codecs
import jinja2
import os.path
from urllib.parse import urlparse
import yaml
from publicstatic import conf
from publicstatic import const
from publicstatic import logger
from publicstatic import helpers
from publicstatic import minify
from publicstatic import pathes

_env = None

JINJA_EXTENSIONS = [
    'jinja2.ext.loopcontrols',
]


def env():
    global _env
    if _env is None:
        search_pathes = [pathes.templates(), pathes.theme_templates()]
        logger.info("templates pathes: [%s]" % ', '.join(search_pathes))
        loader = jinja2.FileSystemLoader(searchpath=search_pathes)
        _env = jinja2.Environment(loader=loader, extensions=JINJA_EXTENSIONS)
        _env.filters.update(custom_filters())
        _env.globals.update(custom_globals())
    return _env


def custom_globals():
    return {
        'asset_exists': asset_exists,
    }


def asset_exists(file_name):
    """Returns True if specified asset exists."""
    asset_exists = os.path.isfile(pathes.assets(file_name))
    return asset_exists or os.path.isfile(pathes.theme_assets(file_name))


def custom_filters():
    """Returns a dictionary of custom extensions for Jinja2."""
    return {
        'trimurl': filter_trimurl,
        'strftime': filter_strftime,
        'isoformat': filter_isoformat,
    }


def filter_strftime(value, format):
    return value.strftime(format)


def filter_isoformat(value):
    return value.isoformat()


def filter_trimurl(value):
    """Trims addressing scheme (protocol) from the specified url."""
    url = urlparse(value)
    return url.netloc + url.path.rstrip('/')


def render(data, template, dest_path):
    """Render data using a specified template to a file."""
    result = env().get_template(template).render(data)
    _save(result, dest_path)


def render_file(path, data, dest_path):
    """Read template from a file, and render it to the destination path."""
    with codecs.open(path, mode='r', encoding='utf-8') as f:
        template = env().from_string(f.read())
    _save(template.render(data), dest_path)


def render_page(page_data, dest_path):
    """This one is tricky. It creates a dynamic template inherited from
    the base template, adds a 'main' block to this template with page content
    inside, and renders the result template to [dest_path]. Boom!"""
    base_template = page_data['page']['template'] + '.html'
    content = page_data['page']['content']
    template = """{%% extends "%s" %%}{%% block main %%}%s{%% endblock %%}"""
    template = template % (base_template, content)
    try:
        template = env().from_string(template)
        html = template.render(page_data)
        _save(html, dest_path)
    except jinja2.exceptions.TemplateNotFound as e:
        message = "page generation failed because template was not found: %s"
        logger.error(message % e)


def render_data(data_file, template):
    data_file = pathes.data(data_file)
    with codecs.open(data_file, mode='r', encoding='utf-8') as f:
        data = yaml.load(f)
    template_file = "_data_%s.html" % template
    result = env().get_template(template_file).render({'data': data})
    return result


def _save(text, dest_path):
    """Apply optional HTML minification to the [text] and save it to file."""
    if conf.get('min_html') and helpers.ext(dest_path) == '.html':
        text = minify.minify_html(text)
    with codecs.open(dest_path, mode='w', encoding='utf-8') as f:
        f.write(text)

# coding: utf-8

"""Jinja2 helpers."""

import jinja2
import codecs
from urllib.parse import urlparse
from publicstatic import conf
from publicstatic import const
from publicstatic import images
from publicstatic import helpers
from publicstatic import minify

_env = None

JINJA_EXTENSIONS = [
    'jinja2.ext.loopcontrols',
]


def env():
    global _env
    if _env is None:
        loader = jinja2.FileSystemLoader(searchpath=conf.get('tpl_path'))
        _env = jinja2.Environment(loader=loader, extensions=JINJA_EXTENSIONS)
        _env.filters.update(custom_filters())
    return _env


def custom_filters():
    """Returns a dictionary of custom extensions for Jinja2."""
    return {
        'datetime': filter_datetime,
        'date': filter_date,
        'isodatetime': filter_isodatetime,
        'trimurl': filter_trimurl,
        'image': filter_image,
    }


def filter_datetime(value):
    return value.strftime(conf.get('page_datetime_format'))


def filter_date(value):
    if callable(value):
        value = value.__call__()
    return value.strftime(conf.get('page_date_format'))


def filter_isodatetime(value):
    return value.isoformat()


def filter_trimurl(value):
    """Trims addressing scheme (protocol) from the specified url."""
    url = urlparse(value)
    return url.netloc + url.path.rstrip('/')


def filter_image(id):
    image = images.get_image(id)
    if image is None:
        return "[image not found: %s]" % str(id)
    else:
        html = "<img src=\"{url}\" width=\"{width}\" " \
               "height=\"{height}\" alt=\"{alt}\">"
        return html.format(**image)


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
    template = """{%% extends "%s" %%}
                  {%% block %s %%}
                  %s
                  {%% endblock %%}"""
    base_template = page_data['page']['template']
    content = page_data['page']['content']
    values = (base_template + '.html', const.MAIN_BLOCK, content)
    template = helpers.unindent(template) % values
    _save(env().from_string(template).render(page_data), dest_path)


def _save(text, dest_path):
    """Apply optional HTML minification to the [text] and save it to file."""
    if conf.get('min_html') and helpers.ext(dest_path) == '.html':
        text = minify.minify_html(text)
    with codecs.open(dest_path, mode='w', encoding='utf-8') as f:
        f.write(text)

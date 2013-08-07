# coding: utf-8

import codecs
import re
import os
from datetime import datetime
from pprint import pformat
from publicstatic import conf
from publicstatic import const
from publicstatic import helpers
from publicstatic import logger

# parse '<key>: <value>' string to (str, str) tuple
RE_PARAM = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", re.I | re.M | re.U)


class SourceFile:
    """Basic abstraction used for static files to be copied w/o processing."""
    def __init__(self, source_type, file_name):
        self._type = source_type.lower()
        dir_path = helpers.source_dir(self._type)
        self._path = os.path.join(dir_path, file_name)
        self._relpath = os.path.relpath(self._path, dir_path)
        self._ext = os.path.splitext(file_name)[1].lower()
        self._ctime = datetime.fromtimestamp(os.path.getctime(self._path))
        self._utime = datetime.fromtimestamp(os.path.getmtime(self._path))
        self._processed = False
        self._data = None
        self._text = None

    def __str__(self):
        """Human-readable string representation."""
        return '\n'.join(["%s: %s" % (k, v) for k, v in [
                ('fullname', self._path),
                ('ext', self._ext),
                ('type', self._type),
                ('ctime', self._ctime.isoformat()),
                ('utime', self._utime.isoformat()),
            ]])

    def type(self):
        return self._type;

    def path(self):
        return self._path

    def rel_path(self):
        return self._relpath

    def ext(self):
        return self._ext

    def basename(self):
        return os.path.basename(self._path)

    def dest(self):
        """Returns fully qualified destination file."""
        return os.path.join(conf.get('build_path'), self.rel_dest())

    def rel_dest(self):
        """Returns relative path to destination file."""
        base, ext = os.path.splitext(self._relpath)
        ext = {'.md': '.html', '.less': '.css'}.get(self._ext, self._ext)
        return base + ext

    def dest_dir(self):
        """Returns fully qualified destination directory path."""
        return os.path.dirname(self.dest())

    def processed(self, value=None):
        if type(value) == bool:
            self._processed = value
        return self._processed

    def text(self):
        """Source file contents."""
        if self._text == None:
            with codecs.open(self._path, 'r') as f:
                self._text = f.read()
        return self._text

    def data(self):
        """Reads a post/page file to dictionary."""
        if self._data == None:
            self._data = self._parse()
        return self._data

    def _parse(self):
        data = SourceFile._commons()

        # extract page header data and content from a list of lines
        # and return the result as key-value couples
        lines = self.text().splitlines()
        for num, line in enumerate(lines):
            match = RE_PARAM.match(line)
            if match:
                data[match.group(1).strip().lower()] = match.group(2).strip()
            else:
                data['content'] = ''.join(lines[num:])
                break

        is_post = self._type == const.POST_TYPE
        default_tpl = conf.get('post_tpl' if is_post else 'page_tpl')
        source_url = "{root}blob/master/{type}/{name}"

        def get_time(field, getter):
            try:
                return helpers.parse_time(data[field])
            except:
                return datetime.fromtimestamp(getter(self.path()))

        data.update({
                'source':
                    self._path,

                'title':
                    data.get('title', helpers.get_h1(data['content'])),

                'template':
                    data.get('template', default_tpl).strip(),

                'author':
                    data.get('author', conf.get('author')).strip(),

                'content':
                    helpers.md(data.get('content', ''),
                               conf.get('markdown_extensions')),
                'tags':
                    SourceFile._tags(data.get('tags', '')),

                'source_url':
                    source_url.format(root=conf.get('source_url'),
                                      type='posts' if is_post else 'pages',
                                      name=self.basename()),

                'created':
                    get_time('created', os.path.getctime),

                'updated':
                    get_time('updated', os.path.getmtime),
            })

        return data

    def _commons():
        """Common data fields for page building."""
        return {
                'root_url': conf.get('root_url'),
                'rel_root_url': conf.get('rel_root_url'),
                'archive_url':
                    conf.get('rel_root_url') + conf.get('archive_page'),
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

    def _tags(value):
        """Parses tags from comma-separaed string, or returns default
        tags set from configuration."""
        tags = list(helpers.xsplit(',', value, strip=True, drop_empty=True))
        for tag in tags or conf.get('default_tags'):
            yield {'name': tag, 'url': helpers.tag_url(tag)}

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
        if self.parseable():
            self._parse()

    def __str__(self):
        """Human-readable string representation."""
        return '\n'.join(["%s: %s" % (k, v) for k, v in [
                ('fullname', self._path),
                ('ext', self._ext),
                ('type', self._type),
                ('created', self.created().isoformat()),
                ('updated', self.updated().isoformat()),
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

    def url(self, full=False):
        """Returns an URL corresponding to the source file."""
        root = conf.get('root_url') if full else conf.get('rel_root_url')
        if self._type == const.POST_TYPE:
            # return conf.get('post_location').format()
            pass
        elif self._type == const.PAGE_TYPE:
            pass
        elif self._type == conf.ASSET_TYPE:
            pass
        else:
            raise Exception('unsupported source file type')
        # post_path(page_data['source'], page_data['created'])
        return root + ''

    def dest_dir(self):
        """Returns fully qualified destination directory path."""
        return os.path.dirname(self.dest())

    def parseable(self):
        """Returns true is specified source tyepe could be parsed."""
        return self._type in [const.PAGE_TYPE, const.POST_TYPE]

    def created(self):
        return self.data('created') if self.parseable() else self._ctime

    def updated(self):
        return self.data('updated') if self.parseable() else self._utime

    def processed(self, value=None):
        if type(value) == bool:
            self._processed = value
        return self._processed

    def text(self):
        """Source file contents."""
        self._check_parseable()
        if not hasattr(self, '_text'):
            with codecs.open(self._path, 'r') as f:
                self._text = f.read()
        return self._text

    def data(self, key=None, default=None):
        """Returns page data as a dictionary, or a single data field
        if key argument specified."""
        self._check_parseable()
        return self._data.get(key, default) if key else self._data

    def _check_parseable(self):
        if not self.parseable():
            raise Exception('illegal source type')

    def _parse(self):
        """Extract page header data and content from a list of lines
        and return the result as key-value couples."""
        self._check_parseable()
        data = SourceFile._commons()
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
        source_url_pattern = "{root}blob/master/{type}/{name}"
        source_url = source_url_pattern.format(root=conf.get('source_url'),
            type='posts' if is_post else 'pages', name=self.basename())
        content = helpers.md(data.get('content', ''),
                             conf.get('markdown_extensions'))

        data.update({
                'source': self._path,
                'title': data.get('title', helpers.get_h1(data['content'])),
                'template': data.get('template', default_tpl),
                'author': data.get('author', conf.get('author')),
                'content': content,
                'tags': SourceFile._tags(data.get('tags', '')),
                'source_url': source_url,
                'created':
                    helpers.parse_time(data.get('created'), self._ctime),
                'updated':
                    helpers.parse_time(data.get('updated'), self._utime),
            })

        self._data = data

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

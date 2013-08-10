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
from publicstatic import urlify

# format for the post source files
POST_NAME_FORMAT = "{year}{month}{day}-{name}.md"

# regular expression to extract {name} from a base name of post source file
RE_POST_NAME = re.compile(r"^[\d_-]*([^\.]*)", re.I|re.M|re.U)


class NotImplementedException(Exception):
    pass


def commons_data():
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


class SourceFile:
    """Basic abstraction used for static files to be copied w/o processing."""
    def __init__(self, file_name):
        self._path = os.path.join(self.source_dir(), file_name)
        self._rel_path = os.path.relpath(self._path, self.source_dir())
        self._ext = os.path.splitext(file_name)[1].lower()
        self._ctime = datetime.fromtimestamp(os.path.getctime(self._path))
        self._utime = datetime.fromtimestamp(os.path.getmtime(self._path))
        self._processed = False
        self._rel_dest = None

    def __str__(self):
        """Human-readable string representation."""
        return '\n'.join(["%s: %s" % (k, v) for k, v in [
                ('class', self.__class__),
                ('fullname', self._path),
                ('created', self.created().isoformat()),
                ('updated', self.updated().isoformat()),
            ]])

    def source_dir(self):
        """Source file directory path."""
        raise NotImplementedException()

    def path(self):
        """Full path to the source file."""
        return self._path

    def rel_path(self):
        """Source file path relative to the source root directory."""
        return self._rel_path

    def basename(self):
        """Source file base name."""
        return os.path.basename(self._path)

    def ext(self):
        """Source file extension with leading dot."""
        return self._ext

    def rel_dest(self):
        """Get relative path to destination file."""
        return self._rel_dest

    def dest(self):
        """Returns fully qualified destination file."""
        return os.path.join(conf.get('build_path'), self.rel_dest())

    def dest_dir(self):
        """Returns fully qualified destination directory path."""
        return os.path.dirname(self.dest())

    def url(self, full=False):
        """Returns an URL corresponding to the source file."""
        root = conf.get('root_url') if full else conf.get('rel_root_url')
        return root + self.rel_dest()

    def created(self):
        return self._ctime

    def updated(self):
        return self._utime

    def processed(self, value=None):
        """Get/set 'processed' flag for the file."""
        if type(value) == bool:
            self._processed = value
        return self._processed

    def _tags(value):
        """Parses tags from comma-separaed string, or returns default
        tags set from configuration."""
        tags = list(helpers.xsplit(',', value, strip=True, drop_empty=True))
        for tag in tags or conf.get('default_tags'):
            yield {'name': tag, 'url': helpers.tag_url(tag)}

    def create():
        """Class function to create new source files of the certain type."""
        raise NotImplementedException()


class ParseableFile(SourceFile):
    """Basic abstraction for parseable source files."""

    # parse '<key>: <value>' string to (str, str) tuple
    _re_param = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", re.I|re.M|re.U)

    def __init__(self, file_name):
        super().__init__(file_name)
        self._data = self._parse()

    def data(self, key=None, default=None):
        """Returns page data as a dictionary, or a single data field
        if key argument specified."""
        data = helpers.mergedicts(self._data, commons_data())
        return data.get(key, default) if key else data

    def text(self):
        """Source file contents."""
        if not hasattr(self, '_text'):
            with codecs.open(self._path, 'r', encoding='utf-8') as f:
                self._text = f.read()
        return self._text

    def created(self):
        return self.data('created')

    def updated(self):
        return self.data('updated')

    def default_template(self):
        raise NotImplementedException()

    def source_url(self):
        """Source file URL."""
        raise NotImplementedException()

    def _split(self):
        """Coarse parser for the source file."""
        result = {}
        lines = self.text().splitlines()
        for num, line in enumerate(lines):
            match = ParseableFile._re_param.match(line)
            if match:
                field = match.group(1).strip().lower()
                result[field] = match.group(2).strip()
            else:
                result['content'] = ''.join(lines[num:])
                break
        return result

    def _parse(self):
        """Extract page header data and content from a list of lines
        and return the result as key-value couples."""
        result = self._split()
        content = helpers.md(result.get('content', ''),
                             conf.get('markdown_extensions'))

        result.update({
                'source': self._path,
                'title': result.get('title', helpers.get_h1(result['content'])),
                'template': result.get('template', self.default_template()),
                'author': result.get('author', conf.get('author')),
                'content': content,
                'tags': SourceFile._tags(result.get('tags', '')),
                'source_url': self.source_url(),
                'created':
                    helpers.parse_time(result.get('created'), self._ctime),
                'updated':
                    helpers.parse_time(result.get('updated'), self._utime),
            })

        return result


class AssetFile(SourceFile):
    def __init__(self, file_name):
        super().__init__(file_name)
        base = os.path.splitext(self._rel_path)[0]
        ext = '.css' if self.ext() == '.less' else self.ext()
        self._rel_dest = base + ext

    def source_dir(self):
        return conf.get('assets_path')


class PageFile(ParseableFile):
    def __init__(self, file_name):
        super().__init__(file_name)
        base = os.path.splitext(self._rel_path)[0]
        ext = '.html' if self.ext() in ['.md', '.markdown'] else self.ext()
        self._rel_dest = base + ext

    def source_dir(self):
        return conf.get('pages_path')

    def default_template(self):
        return conf.get('page_tpl')

    def source_url(self):
        """Source file URL."""
        pattern = "{root}blob/master/{type}/{name}"
        return pattern.format(root=conf.get('source_url'),
                              type='posts',
                              name=self.basename())


class PostFile(ParseableFile):
    def __init__(self, file_name):
        super().__init__(file_name)
        name = RE_POST_NAME.match(self._rel_path).group(1)
        path = conf.get('post_location')
        created = self.created()
        self._rel_dest = path.format(year=created.strftime('%Y'),
                                     month=created.strftime('%m'),
                                     day=created.strftime('%d'),
                                     name=name)

    def source_dir(self):
        return conf.get('posts_path')

    def name(self):
        base, ext = os.path.splitex(os.path.basename(self._rel_path))
        return

    def default_template(self):
        return conf.get('post_tpl')

    def source_url(self):
        """Source file URL."""
        root = conf.get('source_url')
        if not root:
            return None
        pattern = "{root}blob/master/{type}/{name}"
        return pattern.format(root=conf.get('source_url'),
                              type='pages',
                              name=self.basename())

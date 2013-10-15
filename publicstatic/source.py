# coding: utf-8

import codecs
import re
import os
from datetime import datetime
from publicstatic import conf
from publicstatic import const
from publicstatic import helpers
from publicstatic import errors
from publicstatic.urlify import urlify
from publicstatic.markdown import md

# format for the post source files
POST_NAME_FORMAT = "{year}{month}{day}-{name}.md"

# regular expression to extract {name} from a base name of post source file
RE_POST_NAME = re.compile(r"^[\d_-]*([^\.]*)", re.U)


class NotImplementedException(errors.BasicException):
    """required functionality is not implemented"""
    pass


class PageExistsException(errors.BasicException):
    """page with the same name already exists"""
    pass


class Source:
    """Basic abstraction used for static files to be copied w/o processing."""
    def __init__(self, file_name, base_dir):
        """Initialize Source object.

        Arguments:
        @file_name - path to a source file name, relative to base_dir.
        @base_dir - root directory for source files of this kind."""

        self._path = os.path.join(base_dir, file_name)
        self._rel_path = os.path.relpath(file_name, base_dir)
        self._ext = os.path.splitext(file_name)[1].lower()
        self._ctime = datetime.fromtimestamp(os.path.getctime(self._path))
        self._utime = datetime.fromtimestamp(os.path.getmtime(self._path))
        self._processed = False

    def __str__(self):
        """Human-readable string representation."""
        return '\n'.join(["%s: %s" % (k, v) for k, v in [
            ('class', self.__class__),
            ('fullname', self._path),
            ('created', self.created().isoformat()),
            ('updated', self.updated().isoformat()),
        ]])

    @staticmethod
    def create():
        """Class function to create new source files of the certain type."""
        raise errors.NotImplementedException()

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
        raise errors.NotImplementedException()

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


class ParseableSource(Source):
    """Basic abstraction for parseable source files."""

    # parse '<key>: <value>' string to (str, str) tuple
    _re_param = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", re.U)

    def __init__(self, file_name, base_dir):
        super().__init__(file_name, base_dir)
        self._data = self._parse()
        self._tag_names = list([tag['name'] for tag in self._data['tags']])

    def set(self, key, value):
        self._data[key] = value

    def data(self, key=None, default=None):
        """Returns page data as a dictionary, or a single data field
        if key argument specified."""
        if 'url' not in self._data:
            self._data['url'] = self.url(full=True)
            self._data['rel_url'] = self.url(full=False)
        return self._data.get(key, default) if key else self._data

    def text(self):
        """Source file contents."""
        if not hasattr(self, '_text'):
            with codecs.open(self._path, 'r', encoding='utf-8') as f:
                self._text = f.read()
        return self._text

    def created(self):
        return self._data.get('created')

    def updated(self):
        return self._data.get('updated')

    def default_template(self):
        raise errors.NotImplementedException()

    def source_url(self):
        """Source file URL."""
        if not conf.get('source_url'):
            return None
        pattern = "{root}blob/master/{type}/{name}"
        return pattern.format(root=conf.get('source_url'),
                              type=self.source_type(),
                              name=self.basename())

    def source_type(self):
        """Helper function to return 'type' part for source_url()."""
        raise errors.NotImplementedException()

    def has_tag(self, tag):
        """Check if source file has specified tag."""
        return tag in self._tag_names

    def _parse(self):
        """Extract page header data and content from a list of lines
        and return the result as key-value couples."""
        meta, content = ParseableSource._split(self.text())
        meta.update({
            'source': self._path,
            'title': meta.get('title', helpers.get_h1(content)),
            'template': meta.get('template', self.default_template()),
            'author': meta.get('author', conf.get('author')),
            'tags': list(ParseableSource._tags(meta.get('tags', ''))),
            'source_url': self.source_url(),
            'created': helpers.parse_time(meta.get('created'), self._ctime),
            'updated': helpers.parse_time(meta.get('updated'), self._utime),
            'content': md(content.strip()),
        })
        return meta

    @staticmethod
    def _split(text):
        """Coarse parser for the source file."""
        result = {}
        lines = text.splitlines()
        num = 0
        for line in lines:
            match = ParseableSource._re_param.match(line)
            if match:
                field = match.group(1).strip().lower()
                result[field] = match.group(2).strip()
                num += 1
            else:
                break
        return result, '\n'.join(lines[num:])

    @staticmethod
    def _tags(value):
        """Parses tags from comma-separaed string, or returns default
        tags set from configuration."""
        tags = list(helpers.xsplit(',', value, strip=True, drop_empty=True))
        for tag in tags or conf.get('default_tags'):
            yield {'name': tag, 'url': helpers.tag_url(tag)}


class AssetSource(Source):
    def rel_dest(self):
        ext = '.css' if self.ext() == '.less' else self.ext()
        return os.path.splitext(self._rel_path)[0] + ext


class PageSource(ParseableSource):
    def rel_dest(self):
        ext = '.html' if self.ext() in ['.md', '.markdown'] else self.ext()
        return os.path.splitext(self._rel_path)[0] + ext

    @staticmethod
    def create(name, force=False):
        """Creates page file.

        Arguments:
            name -- page name (will be used for file name and URL).
            force -- True to overwrite existing file;
                False to throw exception."""
        page_name = urlify(name, ext_map={ord(u'\\'): u'/'}) + '.md'
        file_name = os.path.join(conf.get('pages_path'), page_name)
        if os.path.exists(file_name) and not force:
            raise PageExistsException(path=file_name)
        created = datetime.now().strftime(conf.get('time_format')[0])
        text = const.PROTO_PAGE
        helpers.newfile(file_name, text.format(title=name, created=created))
        return page_name

    def default_template(self):
        return conf.get('page_tpl')

    def source_type(self):
        return 'pages'


class PostSource(ParseableSource):
    def rel_dest(self):
        name = os.path.basename(self._rel_path).lstrip('0123456789-_')
        name = os.path.splitext(name)[0]
        return PostSource._ymd(conf.get('post_location'), self.created(), name)

    @staticmethod
    def create(name, force=False):
        """Create new post file placeholder with a unique name.

        Arguments:
            name -- post name.
            force -- True to overwrite existing file;
                False to raise an exception."""
        created = datetime.now()
        post_name = urlify(name) or const.UNTITLED_POST
        file_name = PostSource._ymd(POST_NAME_FORMAT, created, post_name)
        post_path = os.path.join(conf.get('posts_path'), file_name)

        count = 0
        while True:
            file_name = helpers.suffix(post_path, count)
            if force or not os.path.exists(file_name):
                created = created.strftime(conf.get('time_format')[0])
                text = const.PROTO_POST
                text = text.format(title=name, created=created)
                helpers.newfile(file_name, text)
                break
            count += 1
        return os.path.basename(file_name)

    def name(self):
        base, ext = os.path.splitex(os.path.basename(self._rel_path))
        return

    def default_template(self):
        return conf.get('post_tpl')

    def source_type(self):
        return 'posts'

    @staticmethod
    def _ymd(pattern, timestamp, name):
        """Fills a string pattern with year, month, date, and name values."""
        return pattern.format(year=timestamp.strftime('%Y'),
                              month=timestamp.strftime('%m'),
                              day=timestamp.strftime('%d'),
                              name=name)

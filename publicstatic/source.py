# coding: utf-8

import os
from datetime import datetime
from pprint import pformat
from publicstatic import conf
from publicstatic import const
from publicstatic import helpers
from publicstatic import logger


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

    def __str__(self):
        """Human-readable string representation."""
        return "\n".join(["%s: %s" % (k, v) for k, v in [
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
        base, ext = os.path.splitext(self._relpath)
        ext = { '.md': '.html', '.less': '.css' }.get(self._ext, self._ext)
        return os.path.join(conf.get('build_path'), base + ext)

    def dest_dir(self):
        """Returns fully qualified destination directory path."""
        return os.path.dirname(self.dest())

    def processed(self, value=None):
        if type(value) == bool:
            self._processed = value
        return self._processed

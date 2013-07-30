# coding: utf-8

import os
from datetime import datetime
from pprint import pformat
from publicstatic import conf
from publicstatic import const
from publicstatic import logger


class SourceFile:
    """Basic abstraction used for static files to be copied w/o processing."""

    def __init__(self, source_type, file_name):
        self._type = source_type.lower()
        self._fullname = os.path.join(self.source_dir(self._type), file_name)
        self._ext = os.path.splitext(file_name)[1]
        self._ctime = datetime.fromtimestamp(os.path.getctime(self._fullname))
        self._utime = datetime.fromtimestamp(os.path.getmtime(self._fullname))


    def __str__(self):
        """Human-readable string representation."""

        return "\n".join(["%s: %s" % (k, v) for k, v in [
                ('fullname', self._fullname),
                ('ext', self._ext)
                ('type', self._type),
                ('ctime', self._ctime.isoformat()),
                ('utime', self._utime.isoformat()),
            ]])


    def source_dir(self, source_type):
        """Returns fully qualified directory for the specified source type."""

        dirs = {
            const.ASSET_TYPE: conf.get('assets_path'),
            const.POST_TYPE: conf.get('posts_path'),
            const.PAGE_TYPE: conf.get('pages_path'),
        }

        try:
            return dirs[source_type]
        except:
            raise Exception('invalid source type')


    def ext(self):
        return self._ext


    def type(self):
        return self._type;

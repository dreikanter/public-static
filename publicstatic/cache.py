# coding: utf-8

import os
from publicstatic import conf
from publicstatic import const
from publicstatic import helpers
from publicstatic import logger
from publicstatic.source import SourceFile

from pprint import pprint

class Cache():
    """Website contents cache."""

    def __init__(self):
        self._cache = []

        source_types = {
                'asset': conf.get('assets_path'),
                'post': conf.get('posts_path'),
                'page': conf.get('pages_path'),
            }

        for source_type, path in source_types.items():
            def save(root, rel):
                source_file = SourceFile(source_type=source_type,
                                         file_name=os.path.join(root, rel))
                self._cache.append(source_file)

            helpers.walk(path, save)

    def items(self):
        return self._cache;


    def funnel(self, source_type=None, ext=None, processed=None):
        """Creates source file filter function."""

        def _funnel(source):
            return (source_type == None or source_type == source.type()) and \
                   (ext == None or ext == source.ext() and \
                   (processed == None or processed == source.processed()))

        return _funnel


    def assets(self, ext=None, processed=None):
        funnel = self.funnel(const.ASSET_TYPE, ext=ext, processed=processed)
        return filter(funnel, self._cache)


    def posts(self):
        return filter(self.funnel(const.POSTS_TYPE, ext), self._cache)


    def pages(self):
        return filter(self.funnel(const.PAGES_TYPE, ext), self._cache)

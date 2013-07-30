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


    def filter_func(self, source_type=None, ext=None):
        """Creates source file filter function."""

        def _filter(source_file):
            return (source_type == None or source_type == s.type()) and \
                   (ext == None or ext == s.ext())

        return _filter


    def assets(self, ext=None):
        return filter(filter_func(const.ASSET_TYPE, ext), self._cache)


    def assets(self, ext=None):
        return filter(filter_func(const.ASSET_TYPE, ext), self._cache)


    def assets(self, ext=None):
        return filter(filter_func(const.ASSET_TYPE, ext), self._cache)

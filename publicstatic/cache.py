# coding: utf-8

import os
from publicstatic import conf
from publicstatic import const
from publicstatic import helpers
from publicstatic import logger
from publicstatic.source import SourceFile, AssetFile, PostFile, PageFile


class Cache():
    """Website contents cache."""

    def __init__(self):
        self._cache = []  # full source files list

        source_types = {
                AssetFile: conf.get('assets_path'),
                PostFile: conf.get('posts_path'),
                PageFile: conf.get('pages_path'),
            }

        for source_type, path in source_types.items():
            def save(root, rel):
                source = source_type(file_name=os.path.join(root, rel))
                self._cache.append(source)

            helpers.walk(path, save)

    def condition(self,
                  source_type=None,
                  ext=None,
                  processed=None,
                  basename=None,
                  dest=None):
        """Creates source file filter function."""
        conditions = []

        if source_type != None:
            conditions.append(lambda source: source_type == type(source))

        if ext != None:
            conditions.append(lambda source: ext == source.ext())

        if processed != None:
            conditions.append(lambda source: processed == source.processed())

        if basename != None:
            conditions.append(lambda source: basename == source.basename())

        if dest != None:
            conditions.append(lambda source: dest == source.rel_dest())

        def _condition(source):
            return all([cond(source) for cond in conditions])

        return _condition

    def assets(self,
               ext=None,
               processed=None,
               basename=None):
        """Get assets."""
        condition = self.condition(AssetFile,
                                   ext=ext,
                                   processed=processed,
                                   basename=basename)
        return filter(condition, self._cache)

    def pages(self, dest=None):
        """Get pages."""
        return filter(self.condition(PageFile, dest=dest), self._cache)

    def posts(self):
        """Get ordered posts."""
        if not hasattr(self, '_posts'):
            self._process_posts()
        return self._posts

    def _process_posts(self):
        posts = list(filter(self.condition(PostFile), self._cache))
        posts.sort(key=lambda item: item.created())

        prev = None
        next = None

        for num, post in enumerate(posts, start=1):
            next = posts[num] if num < len(posts) else None
            post.data('prev_url', prev and prev.url())
            post.data('prev_title', prev and prev.data('title'))
            post.data('next_url', next and next.url())
            post.data('next_title', next and next.data('title'))
            prev = post

        self._posts = posts

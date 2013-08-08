# coding: utf-8

import os
from publicstatic import conf
from publicstatic import const
from publicstatic import helpers
from publicstatic import logger
from publicstatic.source import SourceFile, AssetFile, PostFile, PageFile

from pprint import pprint

class Cache():
    """Website contents cache."""

    def __init__(self):
        # full list of source files
        self._cache = []

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
                  basename=None):
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

    def pages(self):
        """Get pages."""
        return filter(self.condition(PageFile), self._cache)

    def posts(self):
        """Get ordered posts."""
        if not hasattr(self, '_posts'):
            self._process_posts()
        return self._posts

    def _process_posts(self):
        posts = list(filter(PostFile, self._cache))
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

# postloc = conf.get('post_location')
# count = 0
# name = os.path.splitext(self.basename())[0]

# def post_location(suffix):
#     return postloc.format(
#             year=self.created().strftime('%Y'),
#             month=self.created().strftime('%m'),
#             day=self.created().strftime('%d'),
#             name=name.lstrip('0123456789-_') or const.UNTITLED_POST,
#             suffix=("-%d" % count + 1) if suffix > 0 else '',
#         )

# while True:
#     result = post_location(suffix)
#     if result in self._post_files:
#         count += 1
#     else:
#         self._post_names

# while True:
#     result = post_location(suffix)
#     file_name = os.path.basename(result)
#     if file_name in _post_names:
#         count += 1
#         suffix = "-%d" % count
#     else:
#         _post_names.append(file_name)
#         break

# _post_path_cache[source_file] = result
# return result

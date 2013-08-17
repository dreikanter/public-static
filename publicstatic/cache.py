# coding: utf-8

import os
from publicstatic import conf
from publicstatic import helpers
from publicstatic import source


class Cache():
    """Website contents cache."""

    def __init__(self):
        self._cache = []
        for param in ['assets_path', 'posts_path', 'pages_path']:
            helpers.walk(conf.get(param), self._add)

    def condition(self,
                  source_type=None,
                  ext=None,
                  processed=None,
                  basename=None,
                  dest=None):
        """Creates source file filter function."""
        conditions = []

        if source_type is not None:
            conditions.append(lambda source: source_type == type(source))

        if ext is not None:
            conditions.append(lambda source: ext == source.ext())

        if processed is not None:
            conditions.append(lambda source: processed == source.processed())

        if basename is not None:
            conditions.append(lambda source: basename == source.basename())

        if dest is not None:
            conditions.append(lambda source: dest == source.rel_dest())

        def _condition(source):
            return all([cond(source) for cond in conditions])

        return _condition

    def assets(self,
               ext=None,
               processed=None,
               basename=None):
        """Get assets."""
        condition = self.condition(source.AssetFile,
                                   ext=ext,
                                   processed=processed,
                                   basename=basename)
        return filter(condition, self._cache)

    def pages(self, dest=None):
        """Get pages."""
        return filter(self.condition(source.PageFile, dest=dest), self._cache)

    def posts(self):
        """Get ordered posts."""
        if not hasattr(self, '_posts'):
            self._posts = self._get_posts()
        return self._posts

    def tags(self):
        """Return a global list of tags with a number of related pages."""
        if not hasattr(self, '_tags'):
            self._tags = self._get_tags()
        return self._tags

    def data(self, tag=None):
        """Returns everything."""
        return {
            'pages': list([page.data() for page in self.pages()]),
            'posts': list([post.data() for post in self.posts()]),
        }

    def _add(self, root_path, rel_path):
        file_name = os.path.join(root_path, rel_path)
        if root_path == conf.get('assets_path'):
            what = source.AssetFile
        elif root_path == conf.get('pages_path'):
            if source.MultiSource.match(rel_path):
                what = source.MultiSource
            else:
                what = source.PageFile
        elif root_path == conf.get('posts_path'):
            what = source.PostFile
        self._cache.append(what(file_name))

    def _get_posts(self):
        posts = list(filter(self.condition(source.PostFile), self._cache))
        posts.sort(key=lambda item: item.created())
        prev = None
        next = None
        for num, post in enumerate(posts, start=1):
            next = posts[num] if num < len(posts) else None
            post.set('prev_url', prev and prev.url())
            post.set('prev_title', prev and prev.data('title'))
            post.set('next_url', next and next.url())
            post.set('next_title', next and next.data('title'))
            prev = post
        return posts

    def _get_tags(self):
        result = set()
        for page in filter(self.condition(source.ParseableFile), self._cache):
            for tag in page.data('tags'):
                result.append(tag)
        return result

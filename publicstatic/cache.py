# coding: utf-8

import os
from publicstatic import conf
from publicstatic import helpers
from publicstatic.source import ParseableFile, AssetFile, PostFile, PageFile


class Cache():
    """Website contents cache."""

    def __init__(self):
        self._cache = []  # full source files list
        self._tags = {}  # global tags list

        source_types = {
            AssetFile: conf.get('assets_path'),
            PostFile: conf.get('posts_path'),
            PageFile: conf.get('pages_path'),
        }

        pages = []
        posts = []

        for source_type, path in source_types.items():
            def save(root, rel):
                source = source_type(file_name=os.path.join(root, rel))
                self._cache.append(source)
                if isinstance(source, ParseableFile):
                    for tag in [tag['name'] for tag in source.data('tags')]:
                        self._tags[tag] = self._tags.get(tag, 0) + 1
                        if isinstance(source, PageFile):
                            pages.append(source)
                        elif isinstance(source, PostFile):
                            posts.append(source)
            helpers.walk(path, save)

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
        self._posts = posts
        self._data = {
            'pages': list([page.data() for page in pages]),
            'posts': list([post.data() for post in posts]),
        }

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
        return self._posts

    def tags(self):
        """Return a global list of tags with a number of related pages."""
        return self._tags

    def data(self, tag=None):
        """Returns everything."""
        return self._data

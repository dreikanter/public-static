# coding: utf-8

import os
from publicstatic import conf
from publicstatic import const
from publicstatic import helpers
from publicstatic import source


class Cache():
    """Website contents cache."""

    def __init__(self):
        self._cache = []
        gen_assets = os.path.join(conf.generic_dir(), const.ASSETS_DIR)
        def_tpl = conf.get('default_templates')

        def add_src(src_type, path, rel):
            full_path = os.path.join(path, rel)
            # if this asset present in generic assets, skip it
            is_asset = src_type == source.AssetSource
            if def_tpl and is_asset:
                if os.path.isfile(os.path.join(gen_assets, rel)):
                    return
            self._cache.append(src_type(full_path, source_dir=path))

        for src_type in source.order():
            def add(path, rel):
                add_src(src_type, path, rel)
            helpers.walk(src_type.source_dir(), add)

        if conf.get('default_templates'):  # add generic assets
            helpers.walk(gen_assets, add)

    def cond(self,
             source_type=None,
             is_inst=None,
             ext=None,
             processed=None,
             basename=None,
             dest=None,
             tag=None):
        """Creates source file filter function."""
        conditions = []

        if source_type is not None:
            conditions.append(lambda source: source_type == type(source))

        if is_inst is not None:
            conditions.append(lambda source: isinstance(source, is_inst))

        if ext is not None:
            conditions.append(lambda source: ext == source.ext())

        if processed is not None:
            conditions.append(lambda source: processed == source.processed())

        if basename is not None:
            conditions.append(lambda source: basename == source.basename())

        if dest is not None:
            conditions.append(lambda source: dest == source.rel_dest())

        if tag is not None:
            tagged = lambda source: isinstance(source, ParseableSource)
            hastag = lambda source: tagged(source) and source.has_tag(tag)
            conditions.append(lambda source: hastag(source))

        def _condition(source):
            return all([cond(source) for cond in conditions])

        return _condition

    def assets(self,
               ext=None,
               processed=None,
               basename=None):
        """Get assets."""
        condition = self.cond(source.AssetSource,
                                   ext=ext,
                                   processed=processed,
                                   basename=basename)
        return filter(condition, self._cache)

    def pages(self, dest=None):
        """Get pages."""
        return filter(self.cond(source.PageSource, dest=dest), self._cache)

    def posts(self, tag=None):
        """Get ordered posts."""
        if not hasattr(self, '_posts'):
            self._posts = self._get_posts()
        if tag is None:
            return self._posts
        else:
            return list([p for p in self._posts if p.has_tag(tag)])

    def tags(self):
        """Return a global list of tags with a number of related pages."""
        if not hasattr(self, '_tags'):
            self._tags = list(self._get_tags())
            self._tags.sort(key=lambda item: item['name'])
        return self._tags

    def index(self, tag=None):
        """Returns blog index data with optional tag filtering."""
        return list([p.data() for p in self.posts(tag=tag)])

    def full_index(self):
        """Return full site index including posts and pages."""
        index = list(self.posts()) + list(self.pages())
        return list([p.data() for p in index])

    def updated(self):
        """Returns last update timestamp of all source files."""
        return max(source.updated() for source in self._cache)

    def _get_posts(self):
        posts = list(filter(self.cond(source.PostSource), self._cache))
        posts.sort(key=lambda item: item.created(), reverse=True)
        prev = None
        next = None
        for num, post in enumerate(posts, start=1):
            prev = posts[num] if num < len(posts) else None
            post.set('next_url', next and next.url())
            post.set('next_title', next and next.data('title'))
            post.set('prev_url', prev and prev.url())
            post.set('prev_title', prev and prev.data('title'))
            next = post
        return posts

    def _get_tags(self):
        pages = filter(self.cond(is_inst=source.ParseableSource), self._cache)
        tags = set()
        counter = dict()
        for page in pages:
            for tag in page.data('tags'):
                tag = tag['name']
                tags.add(tag)
                counter[tag] = counter.get(tag, 0) + 1
        for tag in tags:
            yield {
                'name': tag,
                'count': counter[tag],
                'url': helpers.tag_url(tag),
            }

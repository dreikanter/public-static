# coding: utf-8

"""Image processing."""

import codecs
import glob
import os
from PIL import Image
import yaml
from publicstatic import conf
from publicstatic import const

# a comment to be placed to the beginning of the index file
INDEX_COMMENT = '# This file is not supposed to be manually updated.\n' \
                '# See [pub image --help] for details.'

_index = None


def _index_path():
    return os.path.join(conf.get('images_path'), const.IMAGES_INDEX)


def _load_index():
    try:
        with codecs.open(_index_path(), mode='r', encoding='utf-8') as f:
            return yaml.load(f.read())
    except:
        return {}


def _save_index(data):
    with codecs.open(_index_path(), mode='w', encoding='utf-8') as f:
        f.write('\n\n'.join([INDEX_COMMENT, yaml.dump(data)]))


def _read_image(file_name):
    """Read metadata from graphic file."""
    width, height = Image.open(file_name, mode='r').size
    images_url = conf.get('rel_root_url') + conf.get('images_location') + '/'
    return {
        'url': images_url + 'placeholder.png',
        'width': 500,
        'height': 250,
        'alt': 'Some annotation',
    }


def get_image(id):
    """Return metadata for specified image id"""
    global _index

    if _index is None:
        _index = _load_index()

    if id not in _index:
        pattern = os.path.join(conf.get('images_path'), "%s.*" % str(id))
        files = glob.glob(pattern)
        if files:
            _index[id] = _read_image(files[0])
            _save_index(_index)

    return _index.get(id, None)

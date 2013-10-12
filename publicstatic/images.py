# coding: utf-8

"""Image processing."""

import glob
import os
import re
from PIL import Image
from publicstatic import conf


def read_image(file_name):
    """Read metadata from graphic file."""
    width, height = Image.open(file_name, mode='r').size
    images_url = conf.get('rel_root_url') + conf.get('images_location')
    return {
        'url': "%s/%s" % (images_url, file_name),
        'width': width,
        'height': height,
    }


def get_image(image_id):
    """Return metadata for specified image id"""
    pattern = os.path.join(conf.get('images_path'), "%s_*.*" % str(image_id))
    files = glob.glob(pattern)
    return read_image(files[0]) if files else None


def all():
    """Generate (id, file_name) tuples for all image files"""
    pattern = re.compile(r"^(\d+)_.*")
    path = conf.get('images_path')
    for file_name in glob.glob(os.path.join(path, "*_*.*")):
        match = pattern.match(os.path.basename(file_name))
        if match:
            image_id = int(match.groups(1)[0])
            yield (image_id, os.path.basename(file_name))

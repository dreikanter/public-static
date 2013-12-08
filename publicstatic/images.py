# coding: utf-8

"""Image processing."""

import glob
import os
import re
# from PIL import Image
from publicstatic import conf


def read_image(file_name):
    """Read metadata from graphic file."""
    pattern = re.compile(r"^\d+_(\d+)x(\d+).*")
    match = pattern.match(file_name)
    if match:
        width, height = match.groups(1), match.group(2)
    else:
    #     width, height = Image.open(file_name, mode='r').size
        width, height = 0, 0
    base_url = conf.get('rel_root_url') + conf.get('images_location')
    return {
        'url': "%s/%s" % (base_url, os.path.basename(file_name)),
        'width': int(width),
        'height': int(height),
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
        base_name = os.path.basename(file_name)
        match = pattern.match(base_name)
        if match:
            image_id = int(match.groups(1)[0])
            yield (image_id, base_name, file_name)

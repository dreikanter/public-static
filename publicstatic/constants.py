# coding: utf-8

import os
import re

CONF_NAME = 'pub.conf'

CONSOLE_FMT = "%(asctime)s %(levelname)s: %(message)s"
CONSOLE_DATE_FMT = "%H:%M:%S"
FILE_FMT = "%(asctime)s %(levelname)s: %(message)s"
FILE_DATE_FMT = "%Y/%m/%d %H:%M:%S"
TIME_FMT = "%Y/%m/%d %H:%M:%S"

GENERIC_PATH = 'generic-site'
GENERIC_PAGES = 'generic-pages'
FEED_DIR = 'feed'

RE_FLAGS = re.I | re.M | re.U
H1_PATTERN = re.compile(r"^\s*#\s*(.*)\s*", RE_FLAGS)
POST_PATTERN = re.compile(r"[\w\\/]+")
URI_SEP_PATTERN = re.compile(r"[^a-z\d\%s]+" % os.sep, RE_FLAGS)
URI_EXCLUDE_PATTERN = re.compile(r"[,.`\'\"\!@\#\$\%\^\&\*\(\)\+]+", RE_FLAGS)
PARAM_PATTERN = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", RE_FLAGS)

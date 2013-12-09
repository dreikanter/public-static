#!/usr/bin/env python
import os
from livereload.task import Task
import functools

WATCH_PATHES = [
    'pages',
    'posts',
    'theme',
    'assets',
]


@functools.partial
def rebuild():
    os.system('pub build')


for path in WATCH_PATHES:
    Task.add(path, rebuild)

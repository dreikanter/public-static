#!/usr/bin/env python
import os
from livereload.task import Task

WATCH_PATHES = [
    'pages',
    'posts',
    'theme',
    'assets',
]


def rebuild_function():
  def rebuild():
    os.system('pub build')
  return rebuild


def rebuild():
  os.system('pub build')


for path in WATCH_PATHES:
    Task.add(path, rebuild_function())

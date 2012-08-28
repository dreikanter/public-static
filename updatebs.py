#!/usr/bin/env python
# coding: utf-8
"""A script to update integrated Twitter Bootstrap"""

import logging
import os
import shutil
import yaml

BS_URL = 'git://github.com/twitter/bootstrap.git'
BS_PATH = 'bootstrap'
CONF = 'updatebs.conf'
H2_PATH = 'hydrogen'

log = logging.getLogger()

if not os.path.isdir(BS_PATH):
    log.info('cloning Twitter Bootstrap from GitHub')
    ret = os.system("git clone -- \"%s\" \"%s\"" % (BS_URL, BS_PATH))
else:
    if not os.path.isdir(os.path.join('BS_PATH', '.git')):
        log.error("'%s' is not a git repo" % BS_PATH)
        exit(1)

    log.info('updating Twitter Bootstrap')
    cwd = os.getcwd()
    os.chdir(BS_PATH)
    ret = os.system('git pull')
    os.chdir(cwd)

log.info("git returned '%d'" % ret)
log.info("reading '%s'" % CONF)

with open(CONF, 'r') as f:
    mapping = yaml.load(f.read())

log.info('got %d items from files mapping configuration')

for item in mapping:
    source = os.path.join(BS_PATH, item['from'])
    dest = os.path.join(H2_PATH, item['to'])
    log.info("  '%s' => '%s'" % (source, dest))

    if not os.path.exists(source):
        log.error('source doesn\'t exists')
        continue

    dir_path, _ = os.path.split

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    if os.path.exists(dest):
        os.remove(dest)

    shutil.copy(source, dest)

log.info('done')

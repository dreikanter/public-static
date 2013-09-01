#!/usr/bin/env python
# coding: utf-8

import os
from setuptools import setup, find_packages
import publicstatic.authoring
from publicstatic.version import get_version


def get_data_files(path):
    files = []
    path = os.path.abspath(path)
    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() not in ['.py', '.pyc']:
                full_path = os.path.join(dirname, filename)
                files.append(os.path.relpath(full_path, path))
    return files


setup(
    name='publicstatic',
    description='Yet another static website builder. A good one.',
    version=get_version(),
    license=publicstatic.authoring.__license__,
    author=publicstatic.authoring.__author__,
    author_email=publicstatic.authoring.__email__,
    url=publicstatic.authoring.__url__,
    long_description=open('README.md').read(),
    platforms=['any'],
    packages=find_packages(),
    package_data={'publicstatic': get_data_files('publicstatic')},
    install_requires=[
        'argh',
        'beautifulsoup4',
        'misaka',
        'jinja2',
        'pyyaml',
        'yuicompressor',
    ],
    entry_points={'console_scripts': ['pub = publicstatic.publicstatic:main']},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
       'Development Status :: 5 - Production/Stable',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: MIT License',
       'Programming Language :: Python',
       'Programming Language :: Python :: 2.7',
       'Programming Language :: Python :: 3.3',
    ],
)

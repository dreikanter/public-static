# encoding: utf-8

import os
import codecs
import publicstatic.authoring
from publicstatic.version import get_version
from setuptools import setup, find_packages
import subprocess as sp


def get_data_files(path):
    """Get package data files."""
    files = []
    path = os.path.abspath(path)
    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() not in ['.py', '.pyc']:
                full_path = os.path.join(dirname, filename)
                files.append(os.path.relpath(full_path, path))
    return files


def get_desc(file_name):
    """Get long description by converting README file to reStructuredText."""
    cmd = "pandoc --from=markdown --to=rst %s" % file_name
    try:
        with sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE) as process:
            return process.stdout.read().decode('utf-8')
    except FileNotFoundError:
        print('pandoc not installed, using readme contents as is')
        with codecs.open(file_name, mode='r', encoding='utf-8') as f:
            return f.read()


setup(
    name='publicstatic',
    description='Yet another static website builder. A good one.',
    version=get_version(),
    license=publicstatic.authoring.__license__,
    author=publicstatic.authoring.__author__,
    author_email=publicstatic.authoring.__email__,
    url=publicstatic.authoring.__url__,
    long_description=get_desc('README.md'),
    platforms=['any'],
    packages=find_packages(),
    package_data={'publicstatic': get_data_files('publicstatic')},
    install_requires=[
        'beautifulsoup4',
        'misaka',
        'jinja2',
        'pyyaml',
        'yuicompressor',
    ],
    entry_points=dict(console_scripts=['pub=publicstatic:main']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
    ],
)

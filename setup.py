#!/usr/bin/env python

import os
from setuptools import setup, find_packages
import hydrogen.authoring


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
    name='hydrogen',
    description='Yet another static website builder.',
    version=hydrogen.authoring.VERSION,
    license=hydrogen.authoring.LICENSE,
    author=hydrogen.authoring.AUTHOR,
    author_email=hydrogen.authoring.EMAIL,
    url=hydrogen.authoring.URL,
    long_description=open('README.md').read(),
    platforms=['any'],
    packages=find_packages(),
    package_data={'hydrogen': get_data_files('hydrogen')},
    install_requires=[
        'markdown',
        'mdx_grid',
        'mdx_smartypants',
        'pystache',
        'baker',
        'yuicompressor',
    ],
    entry_points={'console_scripts': ['h2 = hydrogen.hydrogen:main']},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
       'Development Status :: 5 - Production/Stable',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: MIT License',
       'Programming Language :: Python',
       'Programming Language :: Python :: 2.7',
       # TODO: Test and add other versions
    ],
    dependency_links=[
        'https://github.com/dreikanter/markdown-grid/tarball/master#egg=mdx_grid'
    ],
)

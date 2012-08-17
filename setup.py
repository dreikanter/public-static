#!/usr/bin/env python

import os
from setuptools import setup, find_packages


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
    name='public-static',
    description='Yet another static website builder.',
    version='0.4.8',
    license='MIT',
    author='Alex Musayev',
    author_email='alex.musayev@gmail.com',
    url='http://github.com/dreikanter/public-static',
    long_description=open('README.md').read(),
    platforms=['any'],
    packages=find_packages(),
    package_data={'publicstatic': get_data_files('publicstatic')},
    py_modules=['pub'],
    install_requires=[
        'markdown',
        'mdx_grid',
        'mdx_smartypants',
        'pystache',
        'baker',
        'yuicompressor',
    ],
    entry_points={'console_scripts': ['pub = pub:main']},
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

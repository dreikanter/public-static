#!/usr/bin/env python

from setuptools import setup, find_packages
import pub

setup(
    name=pub.__name__,
    description=pub.__doc__,
    version=pub.__version__,
    license=pub.__license__,
    author=pub.__author__,
    author_email=pub.__email__,
    url=pub.__url__,
    long_description=open('README.md').read(),
    platforms=['any'],
    packages=find_packages(),
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

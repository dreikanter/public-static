#!/usr/bin/env python

from setuptools import setup, find_packages
import ps

setup(
    name=ps.__name__,
    description=ps.__doc__,
    version=ps.__version__,
    license=ps.__license__,
    author=ps.__author__,
    author_email=ps.__email__,
    url=ps.__url__,
    long_description=open('README.md').read(),
    platforms=['any'],
    packages=find_packages(),
    py_modules=['ps'],
    install_requires=[
        'markdown',
        'pystache',
        'baker',
        'yuicompressor'
    ],
    entry_points={'console_scripts': ['ps = ps:main']},
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
)

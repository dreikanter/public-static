# encoding: utf-8

import codecs
import os
from setuptools import setup, find_packages
import subprocess

PACKAGE_NAME = 'publicstatic'
LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))


def get_desc():
    """Get long description by converting README file to reStructuredText."""
    file_name = os.path.join(LOCAL_PATH, 'README.md')
    if not os.path.exists(file_name):
        return ''

    try:
        cmd = "pandoc --from=markdown --to=rst %s" % file_name
        stdout = subprocess.STDOUT
        output = subprocess.check_output(cmd, shell=True, stderr=stdout)
        return output.decode('utf-8')
    except subprocess.CalledProcessError:
        print('pandoc is required for package distribution but not installed')
        return codecs.open(file_name, mode='r', encoding='utf-8').read()


def get_version():
    with open(os.path.join(LOCAL_PATH, PACKAGE_NAME, 'version.py')) as f:
        variables = {}
        exec(f.read(), variables)
        version = variables.get('__version__')
        if not version:
            raise RuntimeError('version definition not found')
        return version


setup(
    name=PACKAGE_NAME,
    description='Yet another static website builder. A good one.',
    version=get_version(),
    license='MIT',
    author='Alex Musayev',
    author_email='alex.musayev@gmail.com',
    url='http://github.com/dreikanter/public-static',
    long_description=get_desc(),
    platforms=['any'],
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'jinja2',
        'markdown >= 2.4',
        'mdx_grid',
        'pygments',
        'pyyaml',
        'yuicompressor',
    ],
    entry_points={
        'console_scripts': [
            'pub = %s:main' % PACKAGE_NAME
        ]
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
    dependency_links=[
        'https://github.com/dreikanter/markdown-grid/tarball/master#egg=mdx_grid-0.2.2'
    ],
)

# encoding: utf-8

import codecs
import os
from setuptools import setup, find_packages
import subprocess


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
    try:
        cmd = "pandoc --from=markdown --to=rst %s" % file_name
        output = subprocess.check_output(cmd, shell=True,
                                         stderr=subprocess.STDOUT)
        return output.decode('utf-8')
    except subprocess.CalledProcessError:
        print('pandoc not installed, using readme contents as is')
        with codecs.open(file_name, mode='r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print("error reading readme file: %s" % str(e))
        exit()


def get_version():
    path = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(path, 'publicstatic/version.txt')
    return open(version_file).read().strip()


setup(
    name='publicstatic',
    description='Yet another static website builder. A good one.',
    version=get_version(),
    license='MIT',
    author='Alex Musayev',
    author_email='alex.musayev@gmail.com',
    url='http://github.com/dreikanter/public-static',
    long_description=get_desc('README.md'),
    platforms=['any'],
    packages=find_packages(),
    package_data={'publicstatic': get_data_files('publicstatic')},
    install_requires=[
        'beautifulsoup4',
        'jinja2',
        'livereload',
        'markdown',
        'mdx_smartypants',
        'mdx_grid',
        'pygments',
        'pyyaml',
        'yuicompressor',
    ],
    entry_points=dict(console_scripts=['pub=publicstatic:main']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
    dependency_links=[
        'https://github.com/dreikanter/markdown-grid/'
        'tarball/master#egg=mdx_grid'
    ],
)

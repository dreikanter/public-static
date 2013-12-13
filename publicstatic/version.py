from os.path import abspath, dirname, join

version_file = join(dirname(abspath(__file__)), 'version.txt')
__version__ = open(version_file).read().strip()

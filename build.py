#!/usr/bin/env python

'''[TBD]'''

from os.path import basename, splitext
import baker

__author__ = "Alex Musayev <http://alex.musayev.com>"
__copyright__ = "Copyright 2012, Subliminal Maintenance Lab."
__license__ = "MIT"
__version__ = "0.0.1"
__status__ = "Development"

DEFAULT_SECTION = splitext(basename(__file__))[0]
DEFAULT_CONF = "%s.ini" % DEFAULT_SECTION
DEFAULT_LOG = "%s.log" % DEFAULT_SECTION

COMMON_PARAMS = {"conf": "Configuration file", "section": "Configuration file section", "log": "Log file"}
COMMON_SHORTOPS = {"conf": "c", "section": "s", "log": "l"}


def joind(d1, d2):
    return dict(d1.items() + d2.items())


def get_conf(conf_file, section):
    # TODO
    return {}


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS, default=True)
def build(conf=DEFAULT_CONF, section=DEFAULT_SECTION, log=DEFAULT_LOG):
    """Generate web content"""
    print("Building site using configuration from %s [%s]" % (conf, section))
    return


@baker.command(shortopts=joind(COMMON_SHORTOPS, {"browse": "b"}),
               params=joind(COMMON_PARAMS, {"browse": "Open in default browser"}))
def preview(conf=DEFAULT_CONF, section=DEFAULT_SECTION, log=DEFAULT_LOG, browse=False):
    '''Run local web server to preview generated web site'''
    return


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def publish(conf=DEFAULT_CONF, section=DEFAULT_SECTION, log=DEFAULT_LOG):
    '''Synchronize remote web server with generated content.'''
    return


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def clear(conf=DEFAULT_CONF, section=DEFAULT_SECTION, log=DEFAULT_LOG):
    '''Delete all generated web content'''
    return


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def publish2(conf=DEFAULT_CONF, section=DEFAULT_SECTION, log=DEFAULT_LOG):
    '''Same as sequential execution of Build and Publish'''
    build(conf, section)
    publish()
    return

baker.run()

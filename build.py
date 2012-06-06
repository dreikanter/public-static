#!/usr/bin/env python

'''[TBD]'''

from os.path import basename, splitext, exists
from pprint import pprint, pformat
from configparser import ConfigParser
from shutil import rmtree
import logging
import baker

__author__ = "Alex Musayev <http://alex.musayev.com>"
__copyright__ = "Copyright 2012, Subliminal Maintenance Lab."
__license__ = "MIT"
__version__ = "0.0.1"
__status__ = "Development"

DEFAULT_SECTION = splitext(basename(__file__))[0]
DEFAULT_CONF = "%s.ini" % DEFAULT_SECTION
DEFAULT_LOG = "%s.log" % DEFAULT_SECTION

COMMON_PARAMS = {
    "config": "Configuration file",
    "section": "Configuration file section",
    "logfile": "Log file"
    }

COMMON_SHORTOPS = {
    "config": "c",
    "section": "s",
    "logfile": "l"
    }

TRUE_VALUES = ['1', 'true', 'yes', 'y']

LOG_CONSOLE_FORMAT = ('%(asctime)s %(levelname)s: %(message)s', '%H:%M:%S')
LOG_FILE_FORMAT = ('%(asctime)s %(levelname)s: %(message)s', '%Y/%m/%d %H:%M:%S')

log = logging.getLogger(__name__)
conf = {}

# Helper functions ============================================================


def joind(d1, d2):
    return dict(d1.items() + d2.items())


def init(conf_file, section, log_file):
    """Gets the configuration values or termanates execution in case of errors"""

    def get_params():
        parser = ConfigParser()
        with open(conf_file, 'rt') as f:
            parser.readfp(f)
        return parser.items(section)

    def get_bool(bool_str):
        return True if bool_str.lower() in TRUE_VALUES else False

    def get_pwd(pwd_str):
        file_prefix = 'file://'
        if pwd_str.startswith(file_prefix):
            with open(pwd_str[len(file_prefix):]) as f:
                return f.readline().strip()
        return pwd_str

    try:
        init_logging(log_file)

    except Exception as e:
        print("Error initializing loggign: " + str(e))

    try:
        result = {item[0]: item[1] for item in get_params()}
        # TODO: Process/update conf values
        return result

    except Exception as e:
        log.error("Error reading configuration: " + str(e))
        log.error("Use --help parameter for command line help")
        exit(1)


def init_logging(log_file):
    global log
    log.setLevel(logging.DEBUG)

    channel = logging.StreamHandler()
    channel.setLevel(logging.DEBUG)
    channel.setFormatter(logging.Formatter(LOG_CONSOLE_FORMAT[0], LOG_CONSOLE_FORMAT[1]))

    log.addHandler(channel)

    if log_file:
        ensure_dir(log_file)
        channel = logging.FileHandler(log_file)
        channel.setLevel(logging.DEBUG)
        channel.setFormatter(logging.Formatter(LOG_FILE_FORMAT[0], LOG_FILE_FORMAT[1]))
        log.addHandler(channel)


def ensure_dir(dir_path):
    d = os.path.dirname(dir_path)
    if not os.path.exists(d):
        os.makedirs(d)


# Baker ccommands =============================================================

@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS, default=True)
def build(config=DEFAULT_CONF, section=DEFAULT_SECTION, logfile=DEFAULT_LOG):
    """Generate web content"""
    log.info("Building site using configuration from %s [%s]" % (conf, section))
    return


@baker.command(shortopts=joind(COMMON_SHORTOPS, {"browse": "b"}),
               params=joind(COMMON_PARAMS, {"browse": "Open in default browser"}))
def preview(config=DEFAULT_CONF, section=DEFAULT_SECTION, logfile=DEFAULT_LOG, browse=False):
    '''Run local web server to preview generated web site'''
    return


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def publish(config=DEFAULT_CONF, section=DEFAULT_SECTION, logfile=DEFAULT_LOG):
    '''Synchronize remote web server with generated content.'''
    return


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def clean(config=DEFAULT_CONF, section=DEFAULT_SECTION, logfile=DEFAULT_LOG):
    '''Delete all generated web content'''

    init(conf, section, logfile)
    log.info("Cleaning output...")

    try:
        if exists(conf['build_path']):
            rmtree(conf['build_path'])
        log.info("Done")

    except Exception as e:
        log.error("Error: " + str(e))


@baker.command(shortopts=COMMON_SHORTOPS, params=COMMON_PARAMS)
def publish2(config=DEFAULT_CONF, section=DEFAULT_SECTION, logfile=DEFAULT_LOG):
    '''Same as sequential execution of Build and Publish'''

    build(conf, section, logfile)
    publish(conf, section, logfile)


baker.run()

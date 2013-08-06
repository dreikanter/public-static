# coding: utf-8

import logging
from logging.handlers import RotatingFileHandler
import os
import os.path
from publicstatic import conf
from publicstatic import const
from publicstatic import helpers

_logger = None


def _check_init():
    if _logger is None:
        init()


def init():
    global _logger
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)
    level = logging.DEBUG if conf.get('verbose') else logging.INFO
    formatter = logging.Formatter(const.LOG_FORMAT, const.LOG_DATE_FORMAT)

    _add_channel(logging.StreamHandler(), level, formatter)

    log_file = conf.get('log_file')
    if log_file:
        helpers.makedirs(os.path.dirname(log_file))
        channel = RotatingFileHandler(log_file,
                                      maxBytes=conf.get('log_max_size'),
                                      backupCount=conf.get('log_backup_cnt'))
        _add_channel(channel, level, formatter)


def _add_channel(channel, level, formatter):
    channel.setLevel(level)
    channel.setFormatter(formatter)
    _logger.addHandler(channel)


def debug(message):
    _check_init()
    _logger.debug(message)


def info(message):
    _check_init()
    _logger.info(message)


def warn(message):
    _check_init()
    _logger.warn(message)


def error(message):
    _check_init()
    _logger.error(message)


def fatal(message):
    _check_init()
    _logger.fatal(message)


def crash():
    """Crash report."""
    import traceback
    import sys
    from datetime import datetime

    message = sys.exc_info()[1]
    with open(const.DUMP_FILE, 'w') as f:
        report = "{generator}, {time}\n\n{message}"
        timestamp = datetime.now().strftime(const.LOG_DATE_FORMAT)
        f.write(report.format(generator=const.GENERATOR,
                              time=timestamp,
                              message=traceback.format_exc()))

    report = "error: %s\nsee %s for details" % (message, const.DUMP_FILE)
    if _logger:
        fatal(report)
    else:
        exit(report)

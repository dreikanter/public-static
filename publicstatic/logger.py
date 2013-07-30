# coding: utf-8

import logging
from logging.handlers import RotatingFileHandler as RFH
import os
import os.path
from publicstatic import conf
from publicstatic import const

_logger = None


def _check_init():
    if _logger is None:
        raise Exception('logger is not initialized')


def init(verbose=False):
    global _logger
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)

    level = logging.DEBUG if verbose or conf.get('verbose') else logging.INFO
    channel = logging.StreamHandler()
    channel.setLevel(level)
    formatter = logging.Formatter(const.LOG_FORMAT, const.LOG_DATE_FORMAT)
    channel.setFormatter(formatter)

    _logger.addHandler(channel)
    log_file = conf.get('log_file')

    if log_file:
        path = os.path.dirname(log_file)
        if path and not os.path.isdir(path):
            os.makedirs(path)

        channel = RFH(log_file,
                      maxBytes=conf.get('log_max_size'),
                      backupCount=conf.get('log_backup_cnt'))

        channel.setLevel(logging.DEBUG)
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

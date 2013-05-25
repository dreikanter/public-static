# coding: utf-8

import logging
import logging.handlers
import os
import os.path
from publicstatic import constants


_logger = None


def _check_init():
    if _logger is None:
        raise Exception('logger is not initialized')


def init(verbose=False):
    global _logger
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)

    level = logging.DEBUG if verbose else logging.INFO
    channel = logging.StreamHandler()
    channel.setLevel(level)
    fmt = logging.Formatter(constants.CONSOLE_FMT, constants.CONSOLE_DATE_FMT)
    channel.setFormatter(fmt)

    _logger.addHandler(channel)


def open_file_channel(log_file, max_size=0, backup_cnt=0):
    if not log_file:
        raise ValueError('log_file')

    global _logger
    _check_init()

    path = os.path.dirname(log_file)
    if path and not os.path.isdir(path):
        os.makedirs(path)

    RFH = logging.handlers.RotatingFileHandler
    channel = RFH(log_file, maxBytes=max_size, backupCount=backup_cnt)
    channel.setLevel(logging.DEBUG)
    fmt = logging.Formatter(constants.FILE_FMT, constants.FILE_DATE_FMT)
    channel.setFormatter(fmt)
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

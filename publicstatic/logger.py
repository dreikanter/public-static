# coding: utf-8

import logging
from logging.handlers import RotatingFileHandler
import os
import os.path
from publicstatic import conf
from publicstatic import const
from publicstatic import helpers

_logger = None


def logger():
    global _logger
    if _logger is None:
        _logger = get_logger()
    return _logger


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    def add_channel(channel):
        level = logging.DEBUG if conf.get('verbose', False) else logging.INFO
        formatter = logging.Formatter(const.LOG_FORMAT, const.LOG_DATE_FORMAT)
        channel.setLevel(level)
        channel.setFormatter(formatter)
        logger.addHandler(channel)

    add_channel(logging.StreamHandler())

    log_file = conf.get('log_file')
    if log_file is not None:
        helpers.makedirs(os.path.dirname(log_file))
        backup_cnt = conf.get('log_backup_cnt', 0)
        max_bytes = conf.get('log_max_size', 0)
        add_channel(RotatingFileHandler(log_file,
                                        maxBytes=max_bytes,
                                        backupCount=backup_cnt))
    return logger


def debug(message):
    logger().debug(message)


def info(message):
    logger().info(message)


def warn(message):
    logger().warn(message)


def error(message):
    logger().error(message)


def fatal(message):
    logger().fatal(message)


def crash():
    """Crash report."""
    import traceback
    logging.critical(traceback.format_exc())

# coding=utf-8
from flask import request
from logging.handlers import RotatingFileHandler
import pickle
import traceback
import logging
import sys
import os
import base64
import time
import inspect
import requests


LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(name)s:  %(levelname)-7s  %(message)s'
LOG_MAXBYTES = 2000000
LOG_BACKUPCOUNT = 10
LOG_ENCODING = 'utf-8'
TIME_FORMAT = '%a, %d %b %Y %H:%M:%S'
ERROR = 'Error'
WARNING = 'Warning'


def notify_webmaster(logger, message):
    payload = {"text": message}

    if logger.environment != "production":
        payload["channel"] = "@noizee"

    requests.post(logger.webhook + hook, json=payload)


def get_time():
    return time.strftime(TIME_FORMAT)


def basepath(file):
    return os.path.abspath(os.path.dirname(file))


def bound_method(obj, method):
    setattr(obj, method.__name__, method.__get__(obj))


def serialized(logger, obj):
    logger.info('data:pickle-serialized encode:base64:\n' +
                base64.b64encode(pickle.dumps(obj)) + '\n')


def get_module_name():
    frm = inspect.stack()[1]
    module = inspect.getmodule(frm[0])
    return module.__name__


"""
    Exceptions ( Errors )
"""


def build_error_message(environment, level, module, error=None):
    message = "*<!channel>*\n"
    message += '[ *{}* ] *System {}* at *{}*.\n'.format(
        environment, level, get_time()
    )

    if bool(error):
        message += '{} `{}` ocurred in `{}`.\n'.format(
            level, error, module
        )

    message += 'Review the application logs for more info.'
    return message


def exception(logger):
    logger.error(traceback.format_exc())


def exception_warn(logger, module):
    logger.warning('Exception has ocurred but current op continues: %s' % module)
    logger.warning(traceback.format_exc())

    message = build_error_message(logger.environment, WARNING, module)
    logger.notify_webmaster(message)


"""
    Flask requests log handlers
"""


def request_finished(logger, sender, response, **extra):
    logger.info(get_time())

    logger.info('Request finished with: "%s" status code.' % (
        str(response.status_code)
    ))

    logger.info('Response data parsed in: "%s"' % request.endpoint)
    logger.info('Data object type: "%s"' % type(response.response))

    if bool(logger.serialize):
        logger.serialized(response.response)


def request_error(logger, sender, exception, **extra):
    logger.error('System failure at %s.' % get_time())
    logger.error('Error ocurred in %s' % request.endpoint)
    logger.exception()

    message = build_error_message(
        logger.environment, ERROR, request.endpoint, exception
    )

    logger.notify_webmaster(message)


"""
    Loggers
"""


def stream_stdout():
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(LOG_LEVEL)
    ch.setFormatter(logging.Formatter(LOG_FORMAT))

    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)
    root.addHandler(ch)


def get_logger(module):
    """Return a logger objject type for the given module name"""
    file_path = os.path.dirname(__file__)
    file_path = os.path.join(file_path, '..', 'log/%s.log' % module)

    handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=LOG_MAXBYTES,
        backupCount=LOG_BACKUPCOUNT,
        encoding=LOG_ENCODING)
    handler.setLevel(LOG_LEVEL)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger = logging.getLogger(module)
    logger.addHandler(handler)

    setattr(logger, 'serialize', 0)
    setattr(logger, "environment", "localhost")
    setattr(logger, "webhook", "http://127.0.0.1")

    bound_method(logger, serialized)
    bound_method(logger, exception)
    bound_method(logger, request_finished)
    bound_method(logger, request_error)
    bound_method(logger, exception_warn)
    bound_method(logger, notify_webmaster)

    return logger

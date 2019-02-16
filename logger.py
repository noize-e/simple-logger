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


msg_formats = {
    'clean': '%(message)s',
    'basic': '[%(asctime)s] %(message)s',
    "extended": '[%(asctime)s] %(name)s:%(levelname)s %(process)6d %(message)s'
}

time_formats = {
    'basic': '%d/%b/%yT%H:%M:%S %Z'
}


def get_time(time_format='%d-%b-%y %H:%M:%S (%Z)'):
    return time.strftime(time_format)


def basepath(file, sublevel=True):
    _basepath = os.path.abspath(os.path.dirname(file))
    if sublevel:
        _basepath = os.path.join(_basepath, '..')
    return _basepath


def bound_method(obj, method):
    setattr(obj, method.__name__, method.__get__(obj))


def serialize(obj, encode=False):
    sobj = pickle.dumps(obj)
    if encode:
        sobj = base64.b64encode(sobj)
    return sobj


def get_module_name():
    print(inspect.stack())
    frm = inspect.stack()[1]
    module = inspect.getmodule(frm[0])
    return module.__name__


"""
    Notifications
"""


def send_webhook(message, webhook='http://127.0.0.1'):
    payload = {'text': message}
    requests.post(webhook, json=payload)


def build_error_message(error, level, module):
    message = '*<!channel>* *System {}!*.\n'.format(
        level, module)
    message += '`{}` ocurred in `{}`.\n'.format(error, module)
    message += 'At *{}*' % get_time()
    return message


def log_and_notify_error(logger, error=None):
    module = get_module_name()
    level = "Error"

    if error:
        logger.error('Exception has ocurred: %s' % module)
        logger.error(traceback.format_exc())
    else:
        logger.warning('Exception has ocurred: %s' % module)
        logger.warning(traceback.format_exc())
        level = "Warning"

    message = build_error_message(error, level, module)
    send_webhook(message, logger.webhook)


"""
    Flask requests log handlers
"""


def request_finished(logger, sender, **kwargs):
    response = kwargs["response"]
    logger.info('Request %s %s ( %s ) endpoint=%s;' % (
        str(request.method),
        str(request.path),
        str(request.query_string or None),
        str(request.endpoint)
    ))
    logger.info('Response %s %s; length=%sb' % (
        str(response.status),
        str(response.content_type),
        str(response.content_length)
    ))


def request_error(logger, sender, exception, **extra):
    logger.exception('Error ocurred in %s' % request.endpoint)
    log_and_notify_error(logger, error=exception)


"""
    Loggers
"""


def logpath(path, name):
    return os.path.join(path, 'log/%s.log' % name)


def stream_stdout(log_level=logging.INFO,
                  msg_format='extended',
                  time_format='basic'):
    """ Stream to the standard output """
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(log_level)
    ch.setFormatter(logging.Formatter(
        msg_formats[msg_format],
        time_formats[time_format]
    ))

    root = logging.getLogger()
    root.setLevel(log_level)
    root.addHandler(ch)


def get_logger(module,
               log_level=logging.INFO,
               msg_format='extended',
               max_bytes=2000000,
               backup_count=10,
               encoding='utf-8',
               time_format='basic'):
    """
        Return a logger objject type for the given module name
    """
    log_path = logpath(basepath(__file__), module)

    log_formatter = logging.Formatter(
        msg_formats[msg_format],
        time_formats[time_format]
    )

    handler = RotatingFileHandler(
        filename=log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding=encoding
    )

    handler.setLevel(log_level)
    handler.setFormatter(log_formatter)

    logger = logging.getLogger(module)
    logger.addHandler(handler)

    setattr(logger, 'environment', 'localhost')

    bound_method(logger, serialize)
    bound_method(logger, request_error)
    bound_method(logger, request_finished)
    bound_method(logger, log_and_notify_error)

    return logger


def downgrade_logger(logname):
    logger = logging.getLogger(logname)
    logger.level = logging.ERROR

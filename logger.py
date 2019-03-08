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


SLACKURL = "https://hooks.slack.com/services/"
WEBHOOK = "T1E6SAEM8/B34368FNY/42DqU1jALJrI9QxBLu4pTgRD"

"""
Log Message Formats
-------------------

...pretty: request-finished

19/Feb/19T18:55:20 CST - ecommerce-api - INFO -
----API Request---------------------------------------
Type: POST /webhooks/easypost
QueryString: None
Endpoint: __module__.<function: name>
Payload Body: {u'property': u'value'}
Response 200 OK text/html; charset=utf-8; length=2b
-------------------------------------------------------

"""

msg_formats = {
    'clean': None,
    'basic': None,
    'pretty': '----{:-<100s}\n{}\n{}{:-<105s}',
    'extended': None
}

logger_formats = {
    'clean': '%(message)s',
    'basic': '[%(asctime)s] %(message)s',
    'pretty': '\n%(asctime)s - %(name)s - %(levelname)s -\n%(message)s',
    'extended': '[%(asctime)s] %(name)s:%(levelname)s %(process)6d %(message)s'
}

time_formats = {
    'basic': '%d/%b/%yT%H:%M:%S %Z',
    'pretty': '%Y-%b-%d %H:%M:%S, %z'
}


"""
    Helpers
"""


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
    obj = pickle.dumps(obj)
    if encode:
        obj = base64.b64encode(sobj)
    return obj


def get_module_name():
    frm = inspect.stack()[1]
    module = inspect.getmodule(frm[0])
    return module.__name__


def clean(string):
    return string.strip('\t\n\r')


"""
    Nofity
"""


def send_webhook(message, webhook=WEBHOOK, url=SLACKURL, channel=None):
    payload = {'text': message}
    if bool(channel):
        payload["channel"] = channel
    slackurl = "%s%s" % (url, webhook)
    requests.post(slackurl, json=payload)


def build_error_message(error, module, environment):
    message = '*<!channel>* *System Error!*.\n'
    message += '`{}` ocurred in `{}`.\n'.format(error, module)
    message += 'At *%s* on *%s*' % (get_time(), environment)
    return message


def log_and_notify_error(logger, error=None, mod=None):
    """ On deprecation """
    module = mod or get_module_name()
    logger.exception('Exception has ocurred: %s' % module)
    if not bool(error):
        error = 'Exception has ocurred: %s' % module
    message = build_error_message(error, module, logger.environment)
    send_webhook(message, logger.webhook)


def notify(logger, error=None, mod=None):
    log_and_notify_error(logger, error, mod)


def breakline(logger, title=' logger.info '):
    logger.info('-----{:-<70s}'.format(title))


"""
    Debug helpers
"""


def debugObject(logger, obj, head=None):
    objstring = "*%s*\n```" % (head or "dictionary:")
    try:
        data = dict(obj.__dict__)
    except:
        data = dict(obj)
    for key, val in data.iteritems():
        objstring += "- {:15s}: {}\n".format(key, str(val))
    objstring += "```"
    return objstring


def debugAlert(logger, message, mod=__name__):
    message = '[DEBUG] %s: %s' % (mod, message)
    logger.debug(message)
    send_webhook(message, channel="@noizee")


"""
    Flask requests log handlers
"""


EXCLUDED_PATHS = [
    str("/api/auth/signin/anon"),
    str("/admin/coupon/"),
    str("/admin/order/"),
    str("/admin/refund/")
]


def get_payload_preview(request, truncate=False):
    try:
        data = request.get_json()

        if "password" in data:
            del data["password"]

        data = repr(data)
        if truncate:
            data = "{:200.200s}".format(data)

        return data
    except:
        return None


def get_querystring(request):
    try:
        query = request.query_string or None
        query = query.strip("?").split("&")
        return ", ".join(query)
    except:
        return None


def get_request_data():
    log = 'Path: %s\n' % str(request.path)
    log += 'Method: %s\n' % str(request.method)
    log += 'QueryString: %s\n' % get_querystring(request)
    log += 'Endpoint: %s\n' % str(request.endpoint)

    payload = get_payload_preview(request)
    if bool(payload):
        log += 'Payload Body:\n\n%s\n' % payload

    return log


def get_response_data(response, log_object=True):
    log = '%s\n' % get_time()
    log += '{:-^100s}\n'.format(" Response ")
    log += 'Status: %s\n' % str(response.status)
    log += 'ContentType: %s\n' % response.content_type
    log += 'ContentLength: %s\n' % response.content_length

    if log_object:
        log += "%s" % repr(response.get_data())
    elif int(response.status_code) in [400, 404, 500]:
        log += "%s.code" % str(response.status_code)
        log += repr(response.get_data())

    return log


def request_finished(logger, sender, **kwargs):
    response = kwargs['response']

    if str(request.path) not in EXCLUDED_PATHS:
        log_request = get_request_data()
        log_response = get_response_data(response)

        logger.info("\n%s" % get_time())
        logger.info("{:=^100s}\n{}\n{}\n{:=^100s}".format(
            ' API Request ', log_request, log_response, " END "
        ))


def request_error(logger, sender, exception, **extra):
    logger.error('\n{}\n{:*^100s}\n{}\n{:*^100s},'.format(
        get_time(), ' ERROR Api Request ', get_request_data(), ''))
    notify(logger, error=exception, mod=request.endpoint)


"""
    Loggers
"""


def logpath(path, name):
    return os.path.join(path, 'log/%s.log' % name)


def stream_stdout(log_level=logging.INFO,
                  logger_format='clean',
                  time_format='basic'):
    """ Stream to the standard output """
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(log_level)
    ch.setFormatter(logging.Formatter(
        logger_formats[logger_format],
        time_formats[time_format]
    ))

    root = logging.getLogger()
    root.setLevel(log_level)
    root.addHandler(ch)


def get_logger(module,
               logger_format='clean',
               time_format='basic',
               log_level=logging.INFO,
               max_bytes=2000000,
               backup_count=10,
               encoding='utf-8',
               environment='localhost',
               webhook=WEBHOOK):
    """
        Return a logger objject type for the given module name
    """
    log_path = logpath(basepath(__file__), module)

    log_formatter = logging.Formatter(
        logger_formats[logger_format],
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

    setattr(logger, 'environment', environment)
    setattr(logger, 'webhook', webhook)
    setattr(logger, 'format', logger_format)

    bound_method(logger, serialize)
    bound_method(logger, request_error)
    bound_method(logger, request_finished)
    bound_method(logger, log_and_notify_error)
    bound_method(logger, notify)
    bound_method(logger, breakline)
    bound_method(logger, debugAlert)
    bound_method(logger, debugObject)

    return logger


def downgrade_logger(logname):
    logger = logging.getLogger(logname)
    logger.level = logging.ERROR

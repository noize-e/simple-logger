simple logger
=============

This module adds configures the pre-built `logging` module from a basic logger configuration to add some extra functionality like after log send a notification.

stream_stdout
-------------

Calling this function set up the log continuity to the standard output even when a logfile handler were configurated.

Usage:

```python
from utils.logger import stream_stdout

# ... application context

stream_stdout()
```

get_logger
----------

This function configures a `logging.Logger` object type with extra __methods bounded to the object instance__. The logger use the `logging.RotatingFileHandler` handler which when the log reach  a pre-defined size it close the log, renames it and opens a new one,  it comes with a default __backup count of 10 each log with a maxium size of 20M__. Each log is __UTF-8__ encoded

```python
from utils.logger import get_logger

# ... application context

logger = get_logger("log-name")
logger.info("This is an info msg")
logger.warning("This is a warning msg")
logger.error("This is an error msg")
```

produces:

```
2019-Feb-20 23:04:39, +0000 - This is an info msg - INFO -
2019-Feb-20 23:04:39, +0000 - This is a warning msg - WARNING -
2019-Feb-20 23:04:39, +0000 - This is an info msg - ERROR -
```

Logging every request with logger and Flask
-------------------------------------------

Import from `flask` module the `got_request_exception` and `request_finished` and pass as first argument the methods __request_finished__ and __request_error__.

Example:

```python
from flask import Flask, got_request_exception, request_finished
from utils.logger import get_logger

application = Flask("app-name")
logger = get_logger("your-log-name")

...

got_request_exception.connect(
  logger.request_error, application)
 

request_finished.connect(
  logger.request_finished, application)
```

`request_finished` produces:

```
21/Feb/19T12:19:09 CST - ecommerce-api - INFO -
----API Request---------------------------------------
Type: POST /api/auth/signin/anon
QueryString: None
Endpoint: api.anon
Payload Body: None
Response 200 OK application/json; length=42b
-------------------------------------------------------
```

`request_error` produces:

```
21/Feb/19T09:29:48 CST - ecommerce-error - ERROR -
----Request Error---------------------------------------------------------------------------------------
Type: GET /api/cart/5c6ebccbb2b85137f50789f1
QueryString: None
Endpoint: api.cart
Payload Body: None
Traceback (most recent call last):
  File "/opt/python/run/venv/local/lib/python2.7/site-packages/flask_restful/__init__.py", line 267, in error_router
    return self.handle_error(e)
  File "/opt/python/run/venv/local/lib/python2.7/site-packages/flask/app.py", line 1817, in wsgi_app
    response = self.full_dispatch_request()
 ...
  File "/opt/python/run/venv/local/lib64/python2.7/site-packages/simplejson/decoder.py", line 400, in raw_decode
    return self.scan_once(s, idx=_w(s, idx).end())
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

Chanelog
--------

- **Feb 06, 2019 - Removed** attributes setters for `logging.logger` instance type, values now taken from the function's arguments.
- **Feb 06, 2019 - Added** new method `downgrade_logger` - sets the log level to error to the given logger.
- Move and added new formats types:
  + `msg-format`: basic, clean, extended.
  + `time-format`: basic.
- **Feb 06, 2019 - Removed**  `exception` function given that logging.logger already has an implementation of it.
- **Feb 06, 2019 - Added** `log_and_notify_error` function.
- **Feb 06, 2019 - Renamed** function `notify_webmaster` now is `log_and_notify_error`
- **Feb 06, 2019 - Decoupled** values validation from logger attributes, like environment or webhook.

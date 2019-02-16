simple logger
=============

This module wrappes the python logging module defining functions for stream to the stdout with a predefied format,create a rotated log file and worth to mention, log every request from Flask API

The module consumes from the environment context the following variables:

- __environment__: current environment where its running the application.
- __logger_serializing__: Enables the serialized and registration of every data container from a finished requests using [Flask]().
- __logger_webhook__: Enables on every finished request to send a notification to a `Slack Webhook`.

Example using `python-dotenv`:

```python
from dotenv import load_dotenv
from utils.logger import get_logger
import os

load_dotenv(verbose=True, override=True)

logger = get_logger("logfile-name")
logger.environment = os.getenv("environment")
logger.serialize = bool(os.getenv('logger_serializing'))
logger.webhook = str(os.getenv('logger_webhook'))
```

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

This function configures and returns a `logging.Logger` object type with some extra `methods bounded to the instance ( not to the class )`.

It uses a `logging.RotatingFileHandler` object type to archive the logfile ( preceding with a number ) when it reachs the (n) of bytes size.

The bounded methods are listed below.

- __serialized__: Given a data container, `serialize ( use pickle library )`, encode in `base64` and register it in a log file.
- __exception__: If this functioon is called insade a try..catch statement, when an exception ocurrs it gras the stack trace from Traceback object type and regiter it inside a log file.
- __exception_warn__: The same functionaility as exception, with the variability of, when set on the slack webhook notification it is considered as a warning and not an error.
- __notify_webmaster__: As we have saw, it performs a `GET request` to a given `Slack Webhook`


Log every succesful or failed request with logger and Flask
-----------------------------------------------------------

To enable this feature just import from flask object the `got_request_exception` and `request_finished`, when calling them, call the __request_finished__ and __request_error__ from logger instance and pass them as arguments within the Flask application.

Example:

```python
from flask import Flask got_request_exception, request_finished
from utils.logger import get_logger

application = Flask("app-name")
logger = get_logger("flask_log")

# ...

got_request_exception.connect(logger.request_error, 
                              application)

request_finished.connect(logger.request_finished, 
                         application)
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

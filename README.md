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
[16/feb/19T13:12:40 CST] log-name:INFO    62346 This is an info msg
[16/feb/19T13:12:40 CST] log-name:WARNING 62346 This is a warning msg
[16/feb/19T13:12:40 CST] log-name:ERROR   62346 This is an error msg
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

Produces:

```
[16/feb/19T13:12:40 CST] ecommerce-api:INFO  62346 Request GET /api/access-point ( key=val&key=val ) endpoint=api.method;
[16/feb/19T13:12:40 CST] ecommerce-api:INFO  62346 Response 200 OK text/html; charset=utf-8; length=1098b
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

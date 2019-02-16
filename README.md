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

Log every succesful or failed request with logger and Flask
-----------------------------------------------------------

Import from `flask` module the `got_request_exception` and `request_finished` and pass as first argument the methods __request_finished__ and __request_error__.

Example:

```python
from flask import Flask, got_request_exception, request_finished
from utils.logger import get_logger

application = Flask("app-name")
logger = get_logger("your-log-name")

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

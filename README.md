```                 _                             
 _ __ ___  _   _| | ___   __ _  __ _  ___ _ __ 
| '_ ` _ \| | | | |/ _ \ / _` |/ _` |/ _ | '__|
| | | | | | |_| | | (_) | (_| | (_| |  __| |   
|_| |_| |_|\__, |_|\___/ \__, |\__, |\___|_|   
           |___/         |___/ |___/      v0.9.1
```

This is a quick introduction to simplogger, as the time allows me to update the documentation, i will try to be more detailed in each setting of the module.

Simplogger defines functions to perform logging using the pre-built python `logging` module but saving us the configuration of each logger.

Required:

[Python2 => 2.7](https://www.python.org/)

Logging
-------

Import the `get_logger` method from `logger.py` and set a name for the logfile and start logging.

The logger has the following settings by default:

- Encode: __UTF-8__
- File Handler: __logging.RotatingFileHandler__
- Max file size: __20M__
- Backup count: __10__


```py
from logger import get_logger

logger = get_logger("log-name")
logger.info("This is an info msg")
logger.warning("This is a warning msg")
logger.error("This is an error msg")
```

Logger & Flask
--------------

Import from `flask` package `got_request_exception & request_finished` methods and setup to use logger's `request_finished & request_error` ones

Example:

```python
from flask import Flask, got_request_exception, request_finished
from utils.logger import get_logger

app = Flask(__name__)
logger = get_logger("my-logger", environment="localhost")

got_request_exception.connect(logger.request_error, app)
request_finished.connect(logger.request_finished, app)
```

###### Request format example
```console
08-Mar-19 15:44:19 (CST)
=========================================== API Request ============================================
Path: /api/payment/5b4fcf2d
Method: PUT
QueryString: None
Endpoint: api.paymentmethod
Payload Body:

{u'function': u'payment', u'value': u'card'}

08-Mar-19 15:44:19 (CST)
--------------------------------------------- Response ---------------------------------------------
Status: 200 OK
ContentType: application/json
ContentLength: 120
'{\n"status": "Ok",\n  "success": "Payment method has been saved"\n}'
=============================================== END ================================================
```

Stdout streamming
-----------------

Import and call `stream_stdout()` function

Usage:

```python
from utils.logger import stream_stdout

stream_stdout()
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

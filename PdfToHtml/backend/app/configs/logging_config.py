import logging
import logging.config
import os
import sys
from datetime import datetime


def setup_logging():
    # Ensure 'logs' directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Get current time
    now = datetime.now()
    log_filename = now.strftime("%Y-%m-%d_%H-%M-%S.log")
    log_filepath = os.path.join('logs', log_filename)
   
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "DEBUG",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "default",
                "level": "DEBUG",
                "filename":  log_filepath,
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(logging_config)

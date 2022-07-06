# import os
import logging.config
import os
import datetime

from .path_config import (
    LOG_ROOT_DIR,
)

timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S_%f')

root_log_file = os.path.join(
    LOG_ROOT_DIR, 'root_debug-%s.log' % timestamp)

log_dirs = [
    LOG_ROOT_DIR,
]

for d in log_dirs:
    if not os.path.exists(d):  # pragma: no cover
        os.makedirs(d)


verbose_format = {
    'format': '%(asctime)s | %(levelname)s | %(message)s | %(process)d %(thread)d | %(filename)s-%(lineno)d:%(funcName)s',
}

basic_format = {
    'format': '%(asctime)s | %(levelname)s | %(message)s | %(filename)s-%(lineno)d',
}


DEBUG_LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    'loggers': {
        'paramiko': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'invoke': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'fabric': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'urllib3': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
        },
        'root_debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': root_log_file,
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'basic': basic_format,
        'verbose': verbose_format,
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'root_debug_file'],
    },
}

logging.config.dictConfig(DEBUG_LOGGING)

logging.info('only INFO logs shows in console. detailed logs: %s' % root_log_file)

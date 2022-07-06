import os

from .constants import (
    PROJECT_ROOT,
)

LOG_ROOT_DIR = os.path.join(PROJECT_ROOT, 'src/logs')

USER_DATA_ROOT = os.path.dirname(PROJECT_ROOT)

# system data dir
EXTRA_DATA_ROOT = os.path.join(USER_DATA_ROOT, 'paper-extra-data')
CRAWLER_CACHE_ROOT = os.path.join(USER_DATA_ROOT, 'paper-crawler-cache')

# user data dir
PAPER_NOTES_DIR = os.path.join(USER_DATA_ROOT, '01-zettelkasten/paper-notes')
PDF_DIR = os.path.join(USER_DATA_ROOT, 'paper-repo/pdfs')

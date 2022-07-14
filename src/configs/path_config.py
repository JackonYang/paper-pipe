import os

from .constants import (
    PROJECT_ROOT,
    PROJECT_SRC_ROOT,
)

LOG_ROOT_DIR = os.path.join(PROJECT_ROOT, 'src/logs')

USER_DATA_ROOT = os.path.dirname(PROJECT_ROOT)

TEMPLATE_DIR = os.path.join(PROJECT_SRC_ROOT, 'templates')
NOTE_TEMPLATE_NAME = 'notes-md.tmpl'

# -------- system data dir --------
EXTRA_DATA_ROOT = os.path.join(USER_DATA_ROOT, 'paper-extra-data')
CRAWLER_CACHE_ROOT = os.path.join(USER_DATA_ROOT, 'paper-crawler-cache')

# reference data dir
# unique dir for each crawler
CRAWLED_SEMANTIC_SCHOLAR_REF_INFO_DIR = os.path.join(CRAWLER_CACHE_ROOT, 'ref-info-semantic-scholar')
# share one dir for collected ref meta
REF_META_DIR = os.path.join(EXTRA_DATA_ROOT, 'ref-meta')

# pdf data dir
PDF_META_DIR = os.path.join(EXTRA_DATA_ROOT, 'pdf-meta')

# -------- user data dir --------
PAPER_NOTES_DIR = os.path.join(USER_DATA_ROOT, '01-zettelkasten/paper-notes')

PDF_DIR = os.path.join(USER_DATA_ROOT, 'paper-repo/pdfs')

import os

from .constants import (
    PROJECT_ROOT,
    PROJECT_SRC_ROOT,
)

LOG_ROOT_DIR = os.path.join(PROJECT_ROOT, 'src/logs')

USER_DATA_ROOT = os.path.dirname(PROJECT_ROOT)
CACHE_DATA_ROOT = os.path.expanduser('~/.cache-paper-reading')

TEMPLATE_DIR = os.path.join(PROJECT_SRC_ROOT, 'templates')
NOTE_TEMPLATE_NAME = 'notes-md.tmpl'

# -------- system data dir --------
EXTRA_DATA_ROOT = os.path.join(CACHE_DATA_ROOT, 'paper-extra-data')
CRAWLER_CACHE_ROOT = os.path.join(CACHE_DATA_ROOT, 'crawler-cache')

# notes config
META_KEY_MAPPING_FILE = os.path.join(EXTRA_DATA_ROOT, 'meta-key-mapping.yaml')

# reference data dir
# unique dir for each crawler
CRAWLED_SEMANTIC_SCHOLAR_REF_INFO_DIR = os.path.join(CRAWLER_CACHE_ROOT, 'ref-info-semantic-scholar')
# share one dir for collected ref meta
REF_META_DIR = os.path.join(EXTRA_DATA_ROOT, 'ref-meta')

# citation data dir
# unique dir for each crawler
CRAWLED_SEMANTIC_SCHOLAR_CITATION_DIR = os.path.join(CRAWLER_CACHE_ROOT, 'citation-semantic-scholar')
# share one dir for collected ref meta
CITATION_META_DIR = os.path.join(EXTRA_DATA_ROOT, 'citation')

# pdf data dir
PDF_META_DIR = os.path.join(EXTRA_DATA_ROOT, 'pdf-meta')

# -------- user data dir --------
PAPER_NOTES_DIR = os.path.join(USER_DATA_ROOT, '01-zettelkasten/paper-notes')

PDF_DIR = os.path.join(USER_DATA_ROOT, 'paper-repo/pdfs')

# -------- export --------
EXPORT_FOR_DIGITAL_PAPER = os.path.join(
    os.path.expanduser('~'), 'digital-paper/paper-reading'
)

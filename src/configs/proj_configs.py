import os

from google.protobuf import text_format

from configs_pb2.crawler_config_pb2 import CrawlerConfig

from .constants import PROJECT_ROOT


# configs API
crawler_config = CrawlerConfig()

# load configs from pb file
crawer_config_pb_path = os.path.join(PROJECT_ROOT, 'pb_conf/crawler_config.pb.txt')

with open(crawer_config_pb_path, 'r') as fr:
    text_format.Parse(fr.read(), crawler_config)


DEFAULT_TAG = os.environ.get('DEFAULT_TAG', 'other-default')
REF_DEFAULT_TAG = os.environ.get('REF_DEFAULT_TAG', 'gen-from-ref')
PDF_DEFAULT_TAG = os.environ.get('PDF_DEFAULT_TAG', 'gen-from-pdf')

TYPE_DEFAULT_TAG = os.environ.get('TYPE_DEFAULT_TAG', 'paper')

DEFAULT_TAG_LIST = [
    DEFAULT_TAG,
    REF_DEFAULT_TAG,
    TYPE_DEFAULT_TAG,
]

# Paper crawler configs
SEED_REF_MIN_COUNTS = [0, 0, 5]
DIGGING_REF_MIN_COUNT = 5

SEED_CITATION_MIN_COUNTS = [0, 30, 30]
CITATION_MAX_PAGES = 3
DIGGING_CITATION_MIN_COUNT = 100

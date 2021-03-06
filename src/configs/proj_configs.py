import os


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
POOLING_REF_MIN_COUNT = 5

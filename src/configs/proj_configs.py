import os


DEFAULT_TAG = os.environ.get('DEFAULT_TAG', 'other-default')

TYPE_DEFAULT_TAG = os.environ.get('TYPE_DEFAULT_TAG', 'paper')

# Paper crawler configs
SEED_REF_MIN_COUNTS = [0, 0, 5]
POOLING_REF_MIN_COUNT = 5

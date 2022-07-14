from .meta_ir_base import MetaIRBase

from configs import (
    REF_META_DIR,
)

ignore_keys = [
    'corpusId',
    'slug',
    'url',
    'badges',
    'numCiting',
    'paperAbstract',
]


class RefMetaIR(MetaIRBase):
    def __init__(self):
        self.meta_dir = REF_META_DIR
        self.name = 'ref_meta'
        self.ignore_keys = ignore_keys

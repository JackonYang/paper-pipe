from .meta_ir_base import MetaIRBase

from configs import (
    REF_META_DIR,
)


class RefMetaIR(MetaIRBase):
    def __init__(self):
        self.meta_dir = REF_META_DIR
        self.name = 'ref_meta'

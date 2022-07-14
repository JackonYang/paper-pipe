import os
from urllib.parse import unquote

from .meta_ir_base import MetaIRBase

from configs import (
    PDF_DIR,
    PDF_META_DIR,
    USER_DATA_ROOT,
)

from utils.files_api import get_file_list


class PdfMetaIR(MetaIRBase):
    def __init__(self):
        self.meta_dir = PDF_META_DIR
        self.name = 'pdf_meta'

    def get_pdf_abs_path(self, pdf_relpath):
        return os.path.join(USER_DATA_ROOT, unquote(pdf_relpath))

    def get_pdf_file_list(self):
        return get_file_list(PDF_DIR, '.pdf')

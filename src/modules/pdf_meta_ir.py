import os
import yaml
from urllib.parse import quote, unquote

from configs import (
    PDF_DIR,
    PDF_META_DIR,
    USER_DATA_ROOT,
)

from utils.files_api import get_file_list


class PdfMetaIR(object):

    def get_pdf_meta_path(self, meta_key):
        return os.path.join(PDF_META_DIR, '%s.yaml' % meta_key)

    def get_pdf_abs_path(self, pdf_relpath):
        return os.path.join(USER_DATA_ROOT, unquote(pdf_relpath))

    def get_meta_file_list(self):
        return get_file_list(PDF_META_DIR, '.yaml')

    def get_pdf_file_list(self):
        return get_file_list(PDF_DIR, '.pdf')

    def get_meta_relpath(self, meta_key):
        meta_path = self.get_pdf_meta_path(meta_key)
        return quote(os.path.relpath(meta_path, USER_DATA_ROOT))

    def save_meta_file(self, meta_key, meta_data):
        meta_path = self.get_pdf_meta_path(meta_key)
        # save meta file
        dirnpath = os.path.dirname(meta_path)
        if not os.path.exists(dirnpath):
            os.makedirs(dirnpath)

        with open(meta_path, 'w') as fw:
            yaml.dump(meta_data, fw)

    def iter_pdf_meta(self):
        for meta_path in self.get_meta_file_list():
            with open(meta_path, 'r') as f:
                meta = yaml.safe_load(f)
            yield meta_path, meta

import os
from urllib.parse import quote

from configs import (
    USER_DATA_ROOT,
)

from utils.files_api import get_file_list
from . import meta_io


class MetaIRBase(object):
    name = None
    meta_dir = None
    ignore_keys = None

    def get_meta_path(self, meta_key):
        return os.path.join(self.meta_dir, '%s.yaml' % meta_key)

    def get_meta_file_list(self):
        return get_file_list(self.meta_dir, '.yaml')

    def get_meta_relpath(self, meta_key):
        meta_path = self.get_meta_path(meta_key)
        return quote(os.path.relpath(meta_path, USER_DATA_ROOT))

    def save_meta_file(self, meta_key, meta_data):
        meta_path = self.get_meta_path(meta_key)
        # save meta file
        dirnpath = os.path.dirname(meta_path)
        if not os.path.exists(dirnpath):
            os.makedirs(dirnpath)

        with open(meta_path, 'w') as fw:
            meta_io.dump(meta_data, fw)

    def iter_meta(self):
        for meta_path in self.get_meta_file_list():
            with open(meta_path, 'r') as f:
                meta = meta_io.safe_load(f)
            yield meta_path, meta

    def is_ignore_key(self, key):
        if not self.ignore_keys:
            return False

        return key in self.ignore_keys

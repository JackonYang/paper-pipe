import os
from urllib.parse import quote

from configs import (
    USER_DATA_ROOT,
)

from utils.files_api import (
    md5_for_file,
    getSizeInNiceString,
)


def filename2key(filename):
    key = filename.replace(' ', '-')
    return key


def extract_info(pdf_path, **kwargs):
    basename = os.path.basename(pdf_path)
    raw_filename, ext = os.path.splitext(basename)

    meta_key = filename2key(raw_filename)
    filesize = os.path.getsize(pdf_path)

    info = {
        'meta_key': meta_key,
        'raw_filename': raw_filename,
        'raw_ext': ext,
        'filesize': filesize,
        'filesize_readable': getSizeInNiceString(filesize),
        'content_md5': md5_for_file(pdf_path),
        'url_slug': quote(raw_filename),
        '%s_relpath' % ext.strip('.'): quote(os.path.relpath(pdf_path, USER_DATA_ROOT)),
    }

    return info

import os
import copy
import shutil
from urllib.parse import unquote

from .base_pipeline import BasePipeline

from modules.note_md_ir import NoteMdIR

from configs import (
    DEFAULT_TAG_LIST,
    EXPORT_FOR_DIGITAL_PAPER,
    USER_DATA_ROOT,
)

import logging

logger = logging.getLogger(__name__)


tags_to_ignore = copy.deepcopy(DEFAULT_TAG_LIST)
tags_to_ignore.extend([
    'book',
    'reading-notes',
])

tags_to_export = [
    'deep-learning-model',
    'compiler',
    'stc',
    'detection',
    'ocr',
    'table-ocr',
]

export_root = EXPORT_FOR_DIGITAL_PAPER


class ExportForDp(BasePipeline, NoteMdIR):

    def run(self, **kwargs):
        copy_cnt = 0

        pdf_root_dir = USER_DATA_ROOT

        for note_path, note_data in self.iter_note_md():
            if 'meta' not in note_data:
                continue

            meta = note_data['meta']

            pdf_relpath = meta.get('pdf_relpath')
            meta_key = meta.get('meta_key')
            tags = meta.get('tags')

            if pdf_relpath is None or meta_key is None or tags is None:
                continue

            pdf_path = os.path.join(pdf_root_dir, unquote(pdf_relpath))

            if not os.path.exists(pdf_path):
                logger.error('file not exists: %s' % pdf_path)
                continue

            for t in tags:

                # white list
                if len(tags_to_export) > 0 and t not in tags_to_export:
                    continue
                # blacklist tags
                if len(tags_to_export) == 0 and t in tags_to_ignore:
                    continue
                out_dir = os.path.join(export_root, t)

                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)

                out_file = os.path.join(out_dir, meta_key + '.pdf')
                # copy if not exists
                if not os.path.exists(out_file):
                    shutil.copyfile(pdf_path, out_file)
                    logger.info('copy: %s -> %s' % (pdf_path, out_file))
                    copy_cnt += 1

        logger.info('%s new files exported to %s' % (copy_cnt, export_root))


pipe_runner_func = ExportForDp().run_all

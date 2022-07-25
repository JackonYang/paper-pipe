import os

from configs import (
    DEFAULT_TAG,
    TYPE_DEFAULT_TAG,
    PDF_DEFAULT_TAG,
)

from .base_pipeline import BasePipeline
from modules.pdf_meta_ir import PdfMetaIR

from processors.info_extractors import (
    file_facts_extractor,
    filename_extractor,
)

import logging

logger = logging.getLogger(__name__)

extractors = [
    file_facts_extractor.extract_info,
    filename_extractor.extract_info,
]


def get_default_tags():
    return [
        DEFAULT_TAG,
        TYPE_DEFAULT_TAG,
        PDF_DEFAULT_TAG,
    ]


class GenPdfMetaPipe(BasePipeline, PdfMetaIR):

    def clean_deleted_meta(self):
        pdf_path_key = 'pdf_relpath'
        for meta_path, meta in self.iter_meta():

            assert pdf_path_key in meta
            pdf_path = self.get_pdf_abs_path(meta[pdf_path_key])
            if not os.path.exists(pdf_path):
                os.remove(meta_path)
                logger.info('pdf not exists. remove meta: %s' % meta_path)

    def gen_metas(self):
        cnt = 0
        for pdf_path in self.get_pdf_file_list():
            self.gen_one_pdf_meta(pdf_path)
            cnt += 1

        logger.info('%s pdf meta saved' % cnt)

    def gen_one_pdf_meta(self, pdf_path):
        meta = {}

        for extractor in extractors:
            meta_patch = extractor(pdf_path=pdf_path, **meta)
            meta.update(meta_patch)

        # tags
        meta.setdefault('tags', get_default_tags())

        # meta_key and meta_relpath
        assert 'meta_key' in meta
        meta_key = meta['meta_key']

        meta['meta_relpath'] = self.get_meta_relpath(meta_key)

        self.save_meta_file(meta_key, meta)

    def run(self, **kwargs):
        self.clean_deleted_meta()
        self.gen_metas()


pipe_runner_func = GenPdfMetaPipe().run_all

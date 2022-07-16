import os
import copy

from .base_pipeline import BasePipeline
from modules.pdf_meta_ir import PdfMetaIR
from modules.ref_meta_ir import RefMetaIR
from modules.note_md_ir import NoteMdIR

from modules.meta_key_mappings import MetaKeyMappings


from configs import (
    REF_DEFAULT_TAG,
    TYPE_DEFAULT_TAG,
)

import logging

logger = logging.getLogger(__name__)

default_reading_status = 'TBD'


class GenNotesMdPipe(BasePipeline, NoteMdIR):
    meta_key_mappings = None

    def __init__(self) -> None:
        super().__init__()

        self.meta_key_mappings = MetaKeyMappings()

    def add_default_meta(self, note_meta):
        note_meta.setdefault('reading_status', default_reading_status)

        if 'tags' not in note_meta:
            note_meta['tags'] = [REF_DEFAULT_TAG, TYPE_DEFAULT_TAG]

    def gen_from_meta_yaml(self, meta_ir):
        tag_list = []

        cnt = 0

        for meta_path, meta in meta_ir.iter_meta():
            assert 'meta_key' in meta
            meta_key = meta['meta_key']

            if self.should_skip(meta_key):
                continue

            note_data = self.load_note_if_exists(meta_key)

            assert 'meta' in note_data
            note_meta = note_data['meta']

            # merge meta
            for k, v in meta.items():
                if not meta_ir.is_ignore_key(k) and k not in note_meta:
                    note_meta[k] = v

            self.add_default_meta(note_meta)

            # hint
            # add ad-hoc logic here if meta needs to be updated

            assert 'tags' in note_meta
            for t in note_meta['tags']:
                if t not in tag_list:
                    tag_list.append(t)

            note_data['meta'] = note_meta

            note_path = self.render_note_md(meta_key, note_data)
            assert note_path is not None

            cnt += 1

        # add_missing_tag_map(tag_list)
        logger.info('%s notes saved from %s yaml.' % (cnt, meta_ir.name))

    def update_merge_mapping(self):

        existed_cnt = self.meta_key_mappings.get_mapping_count()
        scan_cnt = 0

        for note_path, note_data in self.iter_note_md():
            if 'meta' not in note_data or 'meta_key' not in note_data['meta']:
                continue

            scan_cnt += 1

            key_from_meta = note_data['meta']['meta_key']
            key_from_filename = os.path.basename(note_path).replace('.md', '')

            if key_from_filename != key_from_meta:
                self.meta_key_mappings.update_mapping(key_from_filename, key_from_meta)

        new_cnt = self.meta_key_mappings.get_mapping_count()
        logger.info('%s scaned, %s new meta_key mappings to merge.' % (scan_cnt, new_cnt - existed_cnt))

        self.meta_key_mappings.save()

    def merge_notes(self):
        merged = 0
        for src, tar in self.meta_key_mappings.iter_mapping():

            # already merged
            if not self.is_note_exists(src):
                continue

            if not self.is_note_exists(tar):
                self.mv_note(src, tar)
                merged += 1
                continue

            src_data = self.load_note_if_exists(src)
            tar_data = self.load_note_if_exists(tar)

            # set default to avoid exceptions
            tar_data.setdefault('meta', {})
            tar_data.setdefault('content', '')
            src_data.setdefault('meta', {})
            src_data.setdefault('content', '')

            # merge meta info
            # use value in tar if value conflict with src
            merged_meta = copy.deepcopy(tar_data['meta'])
            for k, v in src_data['meta'].items():
                if k not in merged_meta and v is not None:
                    merged_meta[k] = v

            # special keys to merge
            tags = tar_data['meta'].get('tags', []) + src_data['meta'].get('tags', [])
            if len(tags) > 0:
                merged_meta['tags'] = list(set(tags))

            # merge content
            content_list = [
                self.clean_content(src_data['content'], drop_h1_heading=True),
                self.clean_content(tar_data['content'], drop_h1_heading=True),
            ]
            merged_content = '\n\n'.join([i for i in content_list if i is not None and len(i) > 0])

            # merged data
            merged_data = {
                'meta': merged_meta,
                'content': merged_content.strip(),
            }

            note_path = self.render_note_md(tar, merged_data)
            assert note_path
            self.rm_note(src)
            merged += 1

        logger.info('%s new notes mapping merged' % merged)

    def should_skip(self, meta_key):
        return meta_key in self.meta_key_mappings.mapping_dict

    def run(self, skip_gen_note_from_pdf=False, skip_gen_note_from_ref=False, **kwargs):

        if skip_gen_note_from_pdf:
            logger.info('skip generating notes from pdf')
        else:
            self.gen_from_meta_yaml(PdfMetaIR())

        if skip_gen_note_from_ref:
            logger.info('skip generating notes from ref')
        else:
            self.gen_from_meta_yaml(RefMetaIR())

        self.update_merge_mapping()
        self.merge_notes()


pipe_runner_func = GenNotesMdPipe().run_all

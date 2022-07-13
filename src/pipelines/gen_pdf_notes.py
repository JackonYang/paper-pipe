import re
import yaml
import copy
import os

from .base_pipeline import BasePipeline
from modules.pdf_meta_ir import PdfMetaIR
from modules.note_md_ir import NoteMdIR

import logging

logger = logging.getLogger(__name__)

markdown_link_re = re.compile(r'\[(.*?)\]\((.*?)\)')
title_escape_re = re.compile(r'\s*(?:[":]+\s*)+')

h1_heading_re = re.compile(r'^# .*$', re.MULTILINE)

ignore_pdf_meta_keys = [
    'raw_filename',
    'raw_ext',
    'content_md5',
    'filesize',
]

meta_keys_order = [
    'Alias',
    'title',
]

yaml_dump_kwargs = {
    'width': 9999,
    'default_flow_style': False,
}


default_reading_status = 'TBD'


class GenPdfNotesPipe(BasePipeline, PdfMetaIR, NoteMdIR):

    def add_default_meta(self, note_meta):
        note_meta.setdefault('reading_status', default_reading_status)

    def render_meta_str(self, meta):
        heading_meta = copy.deepcopy(meta)
        meta_str = ''
        for k in meta_keys_order:
            if k in heading_meta:
                v = heading_meta.pop(k)
                kv_str = yaml.dump({k: v}, **yaml_dump_kwargs).strip()
                meta_str += '%s\n' % kv_str

        meta_str += yaml.dump(heading_meta, **yaml_dump_kwargs)

        return meta_str.strip()

    def clean_content(self, content, drop_h1_heading=False):
        # TODO(jkyang): refactor this
        if not content or not isinstance(content, str):
            return ''

        content = content.lstrip()

        pdf_link, new_content = content.split('\n', 1)
        if markdown_link_re.match(pdf_link):
            content = new_content.lstrip()

        if drop_h1_heading:
            content = h1_heading_re.sub('', content).lstrip()

        return content

    def gen_from_pdf_yaml(self):
        tag_list = []

        cnt = 0
        relative_root = self.get_relative_root()

        for pdf_meta_path, pdf_meta in self.iter_pdf_meta():
            assert 'meta_key' in pdf_meta
            meta_key = pdf_meta['meta_key']

            if self.should_skip(meta_key):
                continue

            note_data = self.load_note_if_exists(meta_key)

            assert 'meta' in note_data
            note_meta = note_data['meta']

            # merge pdf_meta
            for k, v in pdf_meta.items():
                if k not in ignore_pdf_meta_keys and k not in note_meta:
                    note_meta[k] = v

            self.add_default_meta(note_meta)

            # hint
            # add ad-hoc logic here if meta needs to be updated

            assert 'tags' in note_meta
            for t in note_meta['tags']:
                if t not in tag_list:
                    tag_list.append(t)

            new_meta_str = self.render_meta_str(note_meta)

            note_data['pdf_path'] = os.path.join(relative_root, pdf_meta['pdf_relpath'])
            note_data['meta'] = note_meta
            note_data['meta_str'] = new_meta_str
            note_data['content'] = self.clean_content(note_data['content'])

            note_path = self.render_note_md(meta_key, note_data)
            assert note_path is not None

            cnt += 1

        # add_missing_tag_map(tag_list)
        logger.info('%s notes saved from pdf yaml.' % cnt)

    def should_skip(self, meta_key):
        # TODO(jkyang): add more logic here
        mapping_tasks = {}
        # mapping_tasks = meta_io.read_misc_info(meta_key_mapping_filename)

        return meta_key in mapping_tasks

    def run(self, **kwargs):
        self.gen_from_pdf_yaml()


pipe_runner_func = GenPdfNotesPipe().run_all
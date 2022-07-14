import os
import re
import yaml
import copy
import codecs
from jinja2 import Environment, FileSystemLoader

from configs import (
    PAPER_NOTES_DIR,
    TEMPLATE_DIR,
    NOTE_TEMPLATE_NAME,
    USER_DATA_ROOT,
)

from utils.files_api import get_file_list

META_BOUNDARY = re.compile(r'^-{3,}\s*$', re.MULTILINE)

markdown_link_re = re.compile(r'\[(.*?)\]\((.*?)\)')
h1_heading_re = re.compile(r'^# .*$', re.MULTILINE)


default_data = {
    'meta': {},
    'content': '',
}

ignore_meta_in_heading = [
    'references',
]

meta_keys_order = [
    'Alias',
    'title',
]

yaml_dump_kwargs = {
    'width': 9999,
    'default_flow_style': False,
}


class NoteMdIR(object):
    note_dir = None

    def __init__(self):
        self.note_dir = PAPER_NOTES_DIR

    def get_note_path(self, meta_key):
        return os.path.join(self.note_dir, '%s.md' % meta_key)

    def is_note_exists(self, meta_key):
        return os.path.exists(self.get_note_path(meta_key))

    def get_note_file_list(self):
        return get_file_list(self.note_dir, '.md')

    def get_relative_root(self):
        return os.path.relpath(USER_DATA_ROOT, self.note_dir)

    def render_meta_str(self, meta):
        heading_meta = copy.deepcopy(meta)
        meta_str = ''
        for k in meta_keys_order:
            if k in heading_meta:
                v = heading_meta.pop(k)
                kv_str = yaml.dump({k: v}, **yaml_dump_kwargs).strip()
                meta_str += '%s\n' % kv_str

        for k in ignore_meta_in_heading:
            if k in heading_meta:
                heading_meta.pop(k)

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

    def render_ref_list(self, ref_list):
        str_list = []
        for idx, ref_info in enumerate(ref_list):
            if ref_info['show_ref_link']:
                title_str = '[%s](%s)' % (ref_info['title'], ref_info['meta_key'])
            else:
                title_str = ref_info['title'].strip('][')

            str_list.append(
                '%s. %s' % (idx+1, title_str)
            )
        return str_list

    def fill_paper_ref_info(self, data):
        refs = data['meta'].get('references', [])
        if len(refs) == 0:
            return

        ref_title = 'Paper References'
        data['ref_title'] = ref_title
        data['render_ref_list'] = ref_title.lower() not in data.get('content', '').lower()
        data['ref_str_list'] = self.render_ref_list(refs)

    def is_render_h1(self, data):
        content = data.get('content')
        if content and not h1_heading_re.match(content):
            return True

        if data.get('render_ref_list'):
            return True

        return False

    def render_note_md(self, meta_key, data):
        template_dir = TEMPLATE_DIR,
        template_name = NOTE_TEMPLATE_NAME

        meta = data['meta']

        data['meta_str'] = self.render_meta_str(meta)
        data['content'] = self.clean_content(data['content'])

        pdf_relpath = meta.get('pdf_relpath')
        if pdf_relpath:
            data['pdf_path'] = os.path.join(self.get_relative_root(), pdf_relpath)

        self.fill_paper_ref_info(data)

        # last
        data['render_h1'] = self.is_render_h1(data)

        note_path = self.get_note_path(meta_key)
        env = Environment(
            loader=FileSystemLoader(template_dir),
            keep_trailing_newline=True)
        template = env.get_template(template_name)

        content = template.render(data)

        with codecs.open(note_path, 'w', 'utf8') as f:
            f.write(content)

        return note_path

    def load_note_if_exists(self, meta_key):
        note_path = self.get_note_path(meta_key)

        if os.path.exists(note_path):
            data = self.load_note(note_path)
        else:
            data = copy.deepcopy(default_data)

        return data

    def load_note(self, note_path):
        with open(note_path, 'r') as fr:
            content = fr.read()

        return self.split_content_meta(content)

    def mv_note(self, src, tar):
        src_file = self.get_note_path(src)
        tar_file = self.get_note_path(tar)
        return os.rename(src_file, tar_file)

    def rm_note(self, meta_key):
        os.remove(self.get_note_path(meta_key))

    def split_content_meta(self, content):

        meta = {}

        if META_BOUNDARY.match(content):
            _, fm, content = META_BOUNDARY.split(content, 2)
            meta = yaml.safe_load(fm.strip()) or {}

        data = {
            'meta': meta,
            'content': content.strip(),
        }
        return data

    def iter_note_md(self):
        for note_path in self.get_note_file_list():
            yield note_path, self.load_note(note_path)

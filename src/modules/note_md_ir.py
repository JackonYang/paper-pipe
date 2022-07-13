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

META_BOUNDARY = re.compile(r'^-{3,}\s*$', re.MULTILINE)

default_data = {
    'meta': {},
    'content': '',
}


class NoteMdIR(object):
    def get_note_path(self, meta_key):
        return os.path.join(PAPER_NOTES_DIR, '%s.md' % meta_key)

    def get_relative_root(self):
        return os.path.relpath(USER_DATA_ROOT, PAPER_NOTES_DIR)

    def render_note_md(self, meta_key, data):
        template_dir = TEMPLATE_DIR,
        template_name = NOTE_TEMPLATE_NAME

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

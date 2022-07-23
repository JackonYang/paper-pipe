import os
import re
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

from modules.note_ast import NoteAst
from modules import meta_io


META_BOUNDARY = re.compile(r'^-{3,}\s*$', re.MULTILINE)

# markdown_link_re = re.compile(r'\[(.*?)\]\((.*?)\)')
link_re = r'^\[(.*?%s.*?)\]\((.*?)\)$'
h1_heading_re = re.compile(r'^# (.*)$', re.MULTILINE)

default_data = {
    'meta': {},
    'content': '',
}

leading_links_config = [
    {
        'display': 'pdf(local)',
        'key': 'pdf_path',
    },
    {
        'display': 'semanticscholar url',
        'key': 'semanticscholar_url',
    }
]

leading_links_ptns = [
    re.compile(link_re % re.escape(i['display']), re.MULTILINE)
    for i in leading_links_config
]


class NoteMdIR(object):
    note_dir = None

    def __init__(self):
        self.note_dir = PAPER_NOTES_DIR
        self.note_ast = NoteAst()

    def get_note_path(self, meta_key):
        return os.path.join(self.note_dir, '%s.md' % meta_key)

    def is_note_exists(self, meta_key):
        return os.path.exists(self.get_note_path(meta_key))

    def get_note_file_list(self):
        return get_file_list(self.note_dir, '.md')

    def get_relative_root(self):
        return os.path.relpath(USER_DATA_ROOT, self.note_dir)

    def get_h1(self, data):
        content = data['content']
        m = h1_heading_re.match(content)
        if m:
            return m.group(1).strip()

        if 'title' in data['meta']:
            return data['meta']['title'].strip()

        return ''

    def clean_content(self, content, drop_h1_heading=False):
        # drop leading links
        for ptn in leading_links_ptns:
            content = ptn.sub('', content)

        # drop h1 heading
        if drop_h1_heading:
            content = h1_heading_re.sub('', content)

        # drop leading space
        content = content.lstrip()

        return content

    def is_render_h1(self, data):
        has_content = len(data['h2_sections']) > 0
        has_h1 = len(data.get('h1_heading', '')) > 0

        return has_content and has_h1

    def get_pdf_path_link(self, meta):
        pdf_relpath = meta.get('pdf_relpath')
        if pdf_relpath:
            return os.path.join(self.get_relative_root(), pdf_relpath)

    def get_semanticscholar_url_link(self, meta):
        urls = meta.get('urls')
        if not isinstance(urls, list):
            return

        for url in urls:
            if 'www.semanticscholar.org' in url:
                return url

    def render_note_md(self, meta_key, data):
        template_dir = TEMPLATE_DIR,
        template_name = NOTE_TEMPLATE_NAME

        meta = data['meta']

        # pre-processing
        data['h1_heading'] = self.get_h1(data)
        data['content'] = self.clean_content(data['content'], drop_h1_heading=True)
        # processing
        data['meta_str'] = self.note_ast.render_meta(meta)
        data['h2_sections'] = self.note_ast.gen_h2_sections(data)

        leading_links = []
        for link in leading_links_config:
            meth = getattr(self, 'get_%s_link' % link['key'].lower())
            url = meth(meta)
            if url is not None:
                name = link['display']
                leading_links.append([name, url])

        # post-processing
        data['render_h1'] = self.is_render_h1(data)
        data['leading_links'] = leading_links

        # render
        note_path = self.get_note_path(meta_key)

        dirpath = os.path.dirname(note_path)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

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
            meta = meta_io.safe_load(fm.strip()) or {}

        data = {
            'meta': meta,
            'content': content.strip(),
        }
        return data

    def iter_note_md(self):
        for note_path in self.get_note_file_list():
            yield note_path, self.load_note(note_path)

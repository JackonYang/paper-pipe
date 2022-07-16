import copy
from modules import meta_io

ignore_meta_in_heading = [
    'references',
    'paperAbstract',
]

meta_keys_order = [
    'Alias',
    'title',
]

h2_section_configs = [
    {
        'key': 'abstract',
        'field_key':  'paperAbstract',
        'title': 'Abstract',
        'default_value': '',
    },
    {
        'key': 'content',
    },
    {
        'key': 'ref_list',
        'field_key': 'references',
        'title': 'Paper References',
        'default_value': [],
    },

]


class NoteAst(object):
    def __init__(self) -> None:
        pass

    def render_meta(self, meta):
        heading_meta = copy.deepcopy(meta)

        # keep order consistent between pipelines
        if 'tags' in heading_meta:
            heading_meta['tags'] = sorted(heading_meta['tags'])

        meta_str = ''
        for k in meta_keys_order:
            if k in heading_meta:
                v = heading_meta.pop(k)
                kv_str = meta_io.dump({k: v}).strip()
                meta_str += '%s\n' % kv_str

        for k in ignore_meta_in_heading:
            if k in heading_meta:
                heading_meta.pop(k)

        meta_str += meta_io.dump(heading_meta)

        return meta_str.strip()

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
        return '\n'.join(str_list)

    def gen_section_content(self, data, **kwargs):
        content = data.get('content', '')
        if not content or len(content) == 0:
            return

        info_dict = {
            'value': content,
        }

        return info_dict

    def gen_section_default(self, data, key, field_key, title, default_value, **kwargs):
        info_value = data['meta'].get(field_key, default_value)

        if len(info_value) == 0:
            return

        query = '## %s' % title.lower()
        if query in data.get('content', '').lower():
            return

        render_meth = getattr(self, 'render_%s' % key, None)
        if render_meth:
            info_value = render_meth(info_value)

        info_dict = {
            'title': title,
            'value': info_value.strip(),
        }

        return info_dict

    def gen_section_info(self, _=None, key=None, **kwargs):
        assert _ is None, 'calling gen_section_info with kwargs only'

        meth_name = 'gen_section_%s' % key
        meth = getattr(self, meth_name, self.gen_section_default)

        return meth(key=key, **kwargs)

    def gen_h2_sections(self, data):
        sections = []
        for sec_kwargs in h2_section_configs:
            sections.append(self.gen_section_info(data=data, **sec_kwargs))

        return [i for i in sections if i]

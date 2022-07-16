from configs import (
    CRAWLED_SEMANTIC_SCHOLAR_REF_INFO_DIR as CRAWLED_REF_INFO_DIR,
    REF_META_DIR,
)
import json
import os
import re
import yaml
import copy

from modules.key_generator import gen_meta_key

import logging

logger = logging.getLogger(__name__)


CUR_DIR = os.path.abspath(os.path.dirname(__file__))

multi_space_re = re.compile(r' \s+')


def clean_title_encoding(title):
    # TODO(jkyang): use api in text pipeline
    title = title.replace('–', '-')
    title = title.replace('—', '-')
    title = title.replace('’', '\'')
    title = title.replace('"', '')
    title = title.replace(':', ' - ')

    title = multi_space_re.sub(' ', title)
    return title


def init_raw_paper_dict(dirpath):
    assert os.path.exists(dirpath)

    paper_info = {}
    for file_path in os.listdir(dirpath):
        if not file_path.endswith('.json'):
            continue

        pid = file_path.split('-')[-1].split('.')[0]
        with open(os.path.join(dirpath, file_path), 'r') as f:
            data = json.load(f)

        paper_info[pid] = data

    return paper_info


def save_yaml(paper_info, dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    for pid, info in paper_info.items():
        with open(os.path.join(dirpath, '%s.yaml' % pid), 'w') as f:
            yaml.safe_dump(info, f)


def clean_ref(old_ref):
    if isinstance(old_ref, str):
        return old_ref

    if 'fragments' in old_ref:
        return old_ref['text']

    if isinstance(old_ref, dict):
        return clean_dict(old_ref)

    if isinstance(old_ref, list):
        return [clean_ref(x) for x in old_ref]

    logger.warning("error. unknown: %s" % old_ref)


def clean_dict(old_ref):

    ref = copy.deepcopy(old_ref)
    for k, v in ref.items():
        if k == 'authors':
            ref[k] = [i[-1]['text'] for i in v]
        elif isinstance(v, dict) and 'fragments' in v:
            ref[k] = v['text']
        elif isinstance(v, list):
            ref[k] = [clean_ref(x) for x in v]
        else:
            ref[k] = v

    return ref


ref_cnt_thre = [
    (2015, 100),
    (2010, 1000),
    (2000, 3000),
    (1990, 10000),
    (1950, 30000),
]


def is_drop_by_cited_cnt(cited_cnt, year):
    for y, thre in ref_cnt_thre:
        if year > y:
            return cited_cnt < thre

    return True


def is_drop_by_title(title, meta_key, cited_cnt):
    min_title_length = 10
    # extra year info length: 5
    if len(meta_key) < min_title_length + 5:
        logger.debug('drop title by length. %s' % title)
        return True

    if not meta_key.isascii():
        logger.debug('drop title by non-ascii. %s' % title)
        return True

    if not title.isascii():
        logger.warning('non ascii title: %s' % title)
    elif '"' in title:
        logger.warning('error title: %s' % title)

    return False


def add_info_by_ref(ref_info, new_info):
    ignore_fields = [
        'isKey',
        'citationContexts',
        'tldr',
    ]

    for k, v in ref_info.items():
        if k not in ignore_fields:
            new_info[k] = v


def get_info_from_raw(data):
    if 'meta_info' not in data:
        logger.debug('drop paper. no meta_info. %s' % data)
        return

    if data['meta_info'].get('responseType') == 'CANONICAL':
        return

    if 'totalCitations' in data['meta_info']:
        ref_cnt = data['meta_info']['totalCitations']
    else:
        logger.warning('totalCitations not found: %s' % data)
        ref_cnt = -1

    if 'page_url' not in data:
        logger.warning('no page_url: %s' % data)
        url = ''
    else:
        url = data['page_url']

    return {
        'url': url,
        'ref_count': ref_cnt,
    }


def main():
    raw_paper_info = init_raw_paper_dict(CRAWLED_REF_INFO_DIR)

    paper_info = {}  # yaml map to save
    paper_ref_map = {}

    for cur_pid, data in raw_paper_info.items():

        if 'page_url' not in data:
            continue

        paper_ref_map[cur_pid] = []
        paper_refs = paper_ref_map[cur_pid]
        # update info 2
        for ref_idx, ref in enumerate(data['links']):
            if 'id' not in ref:
                continue
            pid = ref.pop('id')
            cited_cnt = ref.get('numCitedBy', -1)
            year = ref.get('year', -1)

            show_ref_link = (
                pid in raw_paper_info and not is_drop_by_cited_cnt(cited_cnt, year)
            )

            ref = clean_ref(ref)
            ref['title'] = clean_title_encoding(ref['title'])
            ref['meta_key'] = gen_meta_key(ref['title'], year)

            if show_ref_link and is_drop_by_title(ref['title'], ref['meta_key'], cited_cnt):
                show_ref_link = False

            if show_ref_link and pid not in paper_info:
                # new golden paper found.
                new_info = get_info_from_raw(raw_paper_info[pid])
                if new_info:
                    paper_info[pid] = new_info
                    add_info_by_ref(ref, paper_info[pid])

            paper_refs.append({
                'pid': pid,
                'title': ref['title'],
                'show_ref_link': show_ref_link,
                'numCitedBy': ref.get('numCitedBy', -1),
                'fieldsOfStudy': ref.get('fieldsOfStudy', []),
                'year': ref.get('year', -1),
                'meta_key': ref['meta_key'],
            })

    for pid, info in paper_info.items():
        info['references'] = paper_ref_map[pid]

    logger.info('final paper cnt: %s, raw paper cnt: %s. saved at: %s' % (
        len(paper_info), len(raw_paper_info), REF_META_DIR))
    save_yaml(paper_info, REF_META_DIR)


if __name__ == '__main__':
    main()

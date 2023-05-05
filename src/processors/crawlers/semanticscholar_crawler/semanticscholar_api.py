import requests
from utils.lib_cache import jcache
import os
import json

import logging

logger = logging.getLogger(__name__)


url_tmpl = 'https://api.semanticscholar.org/graph/v1/paper/%(pid)s/%(key)s?fields=%(fields)s&offset=%(offset)s&limit=%(limit)s'

paper_fileds = ','.join([
    'title',
    'authors',
    'referenceCount',
    'citationCount',
])


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
example_dir = os.path.join(CURRENT_DIR, 'example')


def fetch_paper_references(pid, offset, limit, **kwargs):
    key = 'references'
    return do_request(key, pid, offset, limit)


def fetch_paper_citations(pid, offset, limit, **kwargs):
    key = 'citations'
    return do_request(key, pid, offset, limit)


@jcache
def do_request(key, pid, offset, limit):
    params = {
        'key': key,
        'pid': pid,
        'fields': paper_fileds,
        'offset': offset,
        'limit': limit,
    }

    url = url_tmpl % params
    logger.info('requesting... key: %s, url: %s' % (key, url))
    resp = requests.get(url)
    if resp.status_code != 200:
        return None

    data = resp.json()

    example_file = os.path.join(example_dir, '%s.json' % key)
    if not os.path.exists(example_file):
        os.makedirs(example_dir, exist_ok=True)
        with open(example_file, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)

    return data

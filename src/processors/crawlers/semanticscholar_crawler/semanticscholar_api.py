import requests
from utils.lib_cache import jcache

import logging

logger = logging.getLogger(__name__)


url_tmpl = 'https://api.semanticscholar.org/graph/v1/paper/%(pid)s/%(key)s?fields=%(fields)s&offset=%(offset)s&limit=%(limit)s'

paper_fileds = ','.join([
    'title',
    'authors',
    'referenceCount',
    'citationCount',
])


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
    return resp.json()

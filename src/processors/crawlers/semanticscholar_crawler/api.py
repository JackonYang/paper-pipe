from urllib.parse import quote
from utils.lib_cache import jcache
import requests
import json

import logging

logger = logging.getLogger(__name__)


@jcache
def send_refs(pid, offset, referer):

    referer = quote(referer, safe='/:?=&')
    logger.debug('sending request... referer: %s' % referer)

    response = requests.get(
        url="https://www.semanticscholar.org/api/1/paper/%s/citations" % pid,
        params={
            "sort": "relevance",
            "offset": "%s" % offset,
            "citationType": "citedPapers",
            "citationsPageSize": "10",
        },
        headers={
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Dnt": "1",
            "Referer": referer,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip",
        },
    )
    return response.json()


def safe_send_refs(pid, offset, page_url):
    try:
        return send_refs(pid, offset, page_url)
    except Exception:
        logger.exception('failed to send request. pid: %s, offset: %s, page_url: %s' % (pid, offset, page_url))
        return None


def default_empty_rsp(page_url, meta_info=None):
    meta_info = meta_info or {}
    return {
        'links': [],
        'meta_info': meta_info,
        'pape_url': page_url,
    }


def download_ref_links(pid, page_url, outfile):

    links = []

    meta_info = safe_send_refs(pid, 0, page_url)
    if not meta_info:
        return default_empty_rsp(page_url)
    elif 'citations' not in meta_info:
        data = default_empty_rsp(page_url, meta_info)
        with open(outfile, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
        return data

    links.extend(meta_info.pop('citations'))
    total_links = meta_info['totalCitations']

    for i in range(10, total_links, 10):
        ret = safe_send_refs(pid, i, page_url)

        if ret is None:
            return default_empty_rsp(page_url)

        links.extend(ret['citations'])

    data = {
        'links': links,
        'meta_info': meta_info,
        'page_url': page_url,
    }

    with open(outfile, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)

    return data

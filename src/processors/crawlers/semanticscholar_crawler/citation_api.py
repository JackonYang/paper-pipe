from urllib.parse import quote
from utils.lib_cache import jcache
import requests
import json

import logging

logger = logging.getLogger(__name__)


@jcache
def send_request(pid, offset, referer):

    referer = quote(referer, safe='/:?=&')

    logger.debug('sending request... referer: %s' % referer)

    url = "https://www.semanticscholar.org/api/1/search/paper/%s/citations" % pid

    response = requests.post(
        url=url,
        headers={
            "Authority": "www.semanticscholar.org",
            "Accept": "*/*",
            "Accept-Language": "zh,zh-CN;q=0.9,en;q=0.8,en-US;q=0.7,zh-TW;q=0.6,fr;q=0.5",
            "Content-Type": "application/json",
            "Dnt": "1",
            "Origin": "https://www.semanticscholar.org",
            "Referer": referer,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip",
        },
        data=json.dumps({
            "pageSize": 10,
            "sort": "total-citations",
            "authors": [],
            "venues": [],
            "yearFilter": None,
            "requireViewablePdf": False,
            "fieldsOfStudy": [],
            "page": offset,
            "coAuthors": [],
            "citationType": "citingPapers"
        })
    )
    try:
        rsp_json = response.json()
    except requests.exceptions.JSONDecodeError:
        logger.warning('parse json error. url: %s' % url)
        rsp_json = None

    return rsp_json


def send_refs(pid, offset, referer):

    referer = quote(referer, safe='/:?=&')
    logger.debug('sending request... referer: %s' % referer)
    url = "https://www.semanticscholar.org/api/1/paper/%s/citations" % pid

    response = requests.get(
        url=url,
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
    try:
        rsp_json = response.json()
    except requests.exceptions.JSONDecodeError:
        logger.warning('parse json error. url: %s' % url)
        rsp_json = None

    return rsp_json


def safe_send_req(pid, offset, page_url):
    try:
        return send_request(pid, offset, page_url)
    except Exception:
        logger.exception('failed to send request. pid: %s, offset: %s, page_url: %s' % (pid, offset, page_url))
        return None


def default_empty_rsp(page_url, meta_info=None):
    meta_info = meta_info or {}
    return {
        'links': [],
        'meta_info': meta_info,
        'page_url': page_url,
    }


def download_citation_links(pid, page_url, outfile, max_pages=None):

    links = []

    meta_info = safe_send_req(pid, 1, page_url)
    if not meta_info:
        return default_empty_rsp(page_url)
    elif meta_info.get('totalPages') == 0:
        data = default_empty_rsp(page_url, meta_info)
        with open(outfile, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
        return data

    links.extend(meta_info.pop('results'))
    total_pages = meta_info['totalPages']

    if max_pages is not None:
        total_pages = min(total_pages, max_pages)

    for i in range(2, total_pages + 1):
        ret = safe_send_req(pid, i, page_url)

        if ret is None:
            return default_empty_rsp(page_url)

        links.extend(ret['results'])

    data = {
        'links': links,
        'meta_info': meta_info,
        'page_url': page_url,
    }

    with open(outfile, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)

    return data

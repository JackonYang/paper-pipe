from urllib.parse import quote
from utils.lib_cache import jcache
import requests
import json

import logging

logger = logging.getLogger(__name__)

url_tmpl = "https://www.semanticscholar.org/api/1/search/paper/%s/citations"
referer_tmpl = '?sort=total-citations&citedSort=%s&citedPage=%s'

@jcache
def send_request(pid, page_no, referer):

    referer_base = referer.split('?', 1)[0]
    sort_alg = 'relevance'
    refer_page_no = page_no - 1 if page_no > 1 else 2
    referer = referer_base + referer_tmpl % (sort_alg, refer_page_no)

    referer = quote(referer, safe='/:?=&')
    url = url_tmpl % pid

    logger.debug('requesting... page: %s, referer: %s' % (page_no, referer))

    response = requests.post(
        url=url,
        headers={
            "Authority": "www.semanticscholar.org",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Referer": referer,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip",
        },
        data=json.dumps({
            "pageSize": 10,
            "sort": sort_alg,
            "authors": [],
            "venues": [],
            "yearFilter": None,
            "requireViewablePdf": False,
            "fieldsOfStudy": [],
            "page": page_no,
            "coAuthors": [],
            "citationType": "citedPapers"
        })
    )

    try:
        rsp_json = response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        logger.warning('parse json error. page_no: %s, pid: %s' % (page_no, pid))
        rsp_json = None

    return rsp_json

from urllib.parse import quote
from utils.lib_cache import jcache
import requests
import json

import logging

logger = logging.getLogger(__name__)


@jcache
def send_request(pid, page_no, referer):

    referer = quote(referer, safe='/:?=&')
    logger.debug('sending request... referer: %s' % referer)

    url = "https://www.semanticscholar.org/api/1/search/paper/%s/citations" % pid

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
            "sort": "relevance",
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

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
    return response.json()

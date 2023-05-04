import copy
import json

from configs_pb2.crawler_config_pb2 import DownloaderConfig

import logging

logger = logging.getLogger(__name__)


# API
def run_downloader(pid: str, page_url: str,
                   api_func: callable, api_configs: DownloaderConfig,
                   outfile: str = None):

    data = _run_downloader(pid, page_url, api_func, api_configs)

    if data is None:
        # ensure the same return schema
        data = wrap_return(page_url)
    elif outfile is not None:
        # save valid data only
        with open(outfile, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)

    return data


def _run_downloader(pid: str, page_url: str,
                    api_func: callable, api_configs: DownloaderConfig):
    start_page = api_configs.start_page
    max_pages = api_configs.max_pages
    links_key = api_configs.links_key_in_response

    links = []

    # step 1, download the first page
    rsp = safe_send_req(api_func, pid, start_page, page_url)

    if rsp is None:
        logger.warning('failed to send request. page_url: %s' % page_url)
        return

    # sucessful response, but no links
    if links_key not in rsp:
        logger.warning('no links in response. links_key: %s, page_url: %s' % (links_key, page_url))
        return wrap_return(page_url, links, rsp)

    total_pages = rsp.get('totalPages', 0)
    if total_pages < 1:
        logger.warning('invalid totalPages in rsp. totalPages: %s, page_url: %s' % (total_pages, page_url))
        return

    # valid response in the first page
    meta_info = copy.deepcopy(rsp)
    links.extend(meta_info.pop(links_key))

    if max_pages is not None and max_pages > 0:
        total_pages = min(total_pages, max_pages)

    # step 2, download the rest pages
    for i in range(start_page + 1, total_pages + 1):
        rsp = safe_send_req(pid, i, page_url)

        if rsp is None:
            return

        # valid response in the rest pages
        links.extend(rsp[links_key])

    return wrap_return(page_url, links, meta_info)


def safe_send_req(api_func, *api_args, **api_kwargs):
    try:
        return api_func(*api_args, **api_kwargs)
    except Exception:
        logger.exception('failed to send request. api_func: %s, api_args: %s, api_kwargs: %s' % (api_func, api_args, api_kwargs))
        return


def wrap_return(page_url, links=None, meta_info=None):
    meta_info = meta_info or {}
    links = links or []

    return {
        'links': links,
        'meta_info': meta_info,
        'page_url': page_url,
    }

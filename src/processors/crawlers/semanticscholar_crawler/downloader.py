import copy
import json

from configs_pb2.crawler_config_pb2 import (
    RequestConfig,
    RequestType,
)

from configs_pb2.api_spec_pb2 import DownloaderTask

from . import request_citation
from . import request_reference

import logging

logger = logging.getLogger(__name__)


req_func_map = {
    RequestType.CITATION: request_citation.send_request,
    RequestType.REFERENCE: request_reference.send_request,
}


# API
def run_tasks(task_args: list[DownloaderTask]):
    task_cnt = len(task_args)
    links = []

    for idx, task in enumerate(task_args):
        data = run_one_task(task)

        new_links = data['links']
        links.extend(new_links)

        req_name = task.request_config.request_type
        msg = '(%s/%s) %s %ss downloaded. url: %s' % (
            idx + 1, task_cnt, len(new_links), req_name, task.page_url)
        logger.info(msg)

    return links


# API
def run_one_task(task: DownloaderTask):

    pid = task.pid
    page_url = task.page_url
    outfile = task.output_file

    req_config = task.request_config
    req_func = req_func_map[req_config.request_type]

    data = _run_downloader(pid, page_url, req_func, req_config)

    if data is None:
        # ensure the same return schema
        data = wrap_return(page_url)
    elif outfile is not None:
        # save valid data only
        with open(outfile, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)

    return data


def _run_downloader(pid: str, page_url: str,
                    api_func: callable, api_configs: RequestConfig):
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
        rsp = safe_send_req(api_func, pid, i, page_url)

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

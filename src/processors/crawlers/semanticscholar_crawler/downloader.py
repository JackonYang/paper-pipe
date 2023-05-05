import json

from configs_pb2.crawler_config_pb2 import (
    RequestConfig,
    RequestType,
)

from configs_pb2.api_spec_pb2 import DownloaderTask

from . import semanticscholar_api

import logging

logger = logging.getLogger(__name__)


req_func_map = {
    RequestType.CITATION: semanticscholar_api.fetch_paper_citations,
    RequestType.REFERENCE: semanticscholar_api.fetch_paper_references,
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
    outfile = task.output_file

    req_config = task.request_config
    req_func = req_func_map[req_config.request_type]

    data = request_by_api(pid, req_func, req_config)

    if data is None:
        # ensure the same return schema
        data = wrap_return(pid)
    elif outfile is not None:
        # save valid data only
        with open(outfile, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)

    return data


def request_by_api(pid: str, api_func: callable, api_configs: RequestConfig):
    max_pages = api_configs.max_pages
    limit = api_configs.limit
    links_key = api_configs.links_key_in_response

    links = []

    offset = 0
    for i in range(max_pages):
        rsp = safe_send_req(api_func, pid, offset=offset, limit=limit)

        if rsp is None:
            logger.warning('failed to send request. page_url: %s' % pid)
            return

        # valid response in the rest pages
        links.extend(rsp[links_key])

        if 'next' not in rsp:
            break

        offset = rsp['next']

    return wrap_return(pid, links)


def safe_send_req(api_func, *api_args, **api_kwargs):
    try:
        return api_func(*api_args, **api_kwargs)
    except Exception:
        logger.exception('failed to send request. api_func: %s, api_args: %s, api_kwargs: %s' % (api_func, api_args, api_kwargs))
        return


def wrap_return(pid, links=None, meta_info=None):
    meta_info = meta_info or {}
    links = links or []

    return {
        'links': links,
        'meta_info': meta_info,
        'pid': pid,
    }

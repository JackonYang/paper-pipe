import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from configs_pb2.crawler_config_pb2 import (
    RequestConfig,
    RequestType,
)

from configs_pb2.api_spec_pb2 import (
    DownloaderTask,
    PaperTask,
)

from . import semanticscholar_api

import logging

logger = logging.getLogger(__name__)


req_func_map = {
    RequestType.CITATION: semanticscholar_api.fetch_paper_citations,
    RequestType.REFERENCE: semanticscholar_api.fetch_paper_references,
}


# API
def run_tasks(task_args: list[PaperTask], log_prefix: str = ''):
    task_cnt = len(task_args)
    links = []
    shared = {
        'done_cnt': 0,
    }

    def run_job(task):
        res_info = {}
        for subtask in task.subtasks:
            data = run_one_task(subtask)

            new_links = data['links']
            links.extend(new_links)

            key = '%s_cnt' % subtask.task_name
            res_info[key] = len(new_links)

        shared['done_cnt'] += 1
        msg = '(%s/%s)%s downloaded %s. title: %s, pid: %s' % (
            shared['done_cnt'], task_cnt, log_prefix,
            str(res_info), task.title, task.pid)

        logger.info(msg)

    with ThreadPoolExecutor(max_workers=5) as t:
        obj_list = []
        for task in task_args:
            obj = t.submit(run_job, task)
            obj_list.append(obj)

        for future in as_completed(obj_list):
            future.result()

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
            logger.warning('failed to send request. pid: %s' % pid)
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

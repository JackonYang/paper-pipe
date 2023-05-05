import os

from configs import (
    crawler_config,
    PROJECT_ROOT,
)

from configs_pb2.api_spec_pb2 import (
    DownloaderTask,
)

from configs_pb2.crawler_config_pb2 import (
    RequestConfig,
    RequestType,
)

from .downloader import run_tasks as run_downloader_tasks

import logging

logger = logging.getLogger(__name__)

conf = crawler_config.semantic_scholar_config


def load_seed_urls():
    seed_file = os.path.join(PROJECT_ROOT, conf.seed_file)

    with open(seed_file, 'r') as f:
        data = f.readlines()

    return [i.strip() for i in data if i.strip()]


def url2pid(url):
    url = url.strip()
    base_url = url.split('?', 1)[0]
    pid = base_url.split('/')[-1]
    return pid


def get_oupout_filename(pid: str, request_config: RequestConfig):
    local_cache_root = os.path.expanduser(crawler_config.local_cache_root)

    output_dir = os.path.join(local_cache_root, request_config.output_dir)

    # ensure output dir exists
    os.makedirs(output_dir, exist_ok=True)

    return os.path.join(output_dir, '%s.json' % pid)


def add_paper_to_tasks(tasks, pid=None, page_url=None) -> int:
    added_cnt = 0

    if [pid, page_url].count(None) != 1:
        raise ValueError('pid and page_url must be set one')

    if pid is None:
        pid = url2pid(page_url)

    added_cnt += add_to_tasks(tasks, RequestType.CITATION, pid)
    added_cnt += add_to_tasks(tasks, RequestType.REFERENCE, pid)

    return added_cnt


def add_to_tasks(tasks: list[DownloaderTask], request_type: RequestType, pid: str) -> int:

    added_cnt = 0

    request_config = None
    for i in conf.request_configs:
        if i.request_type == request_type:
            request_config = i
            break
    if request_config is None:
        raise ValueError('missing request config for %s' % request_type)

    output_file = get_oupout_filename(pid, request_config)

    task = DownloaderTask()
    task.pid = pid
    task.request_config.CopyFrom(request_config)
    task.output_file = output_file

    tasks.append(task)
    added_cnt += 1
    return added_cnt


def find_valuable_links(links_pool, max_count=30):
    return []


def main():
    seed_urls = load_seed_urls()

    links_pool = {}
    valid_links = {}
    valuable_links = {}

    # step 1, download seed_urls ref and citation
    tasks = []
    for url in seed_urls:
        add_paper_to_tasks(tasks, page_url=url)

    new_links = run_downloader_tasks(tasks)
    # links_pool.append(new_links)

    # max_round = 100
    # for round in range(1, max_round+1):
    #     new_tasks = find_valuable_links(links_pool)
    #     logger.info('round (%s/%s), %s new tasks. total links: %s' % (
    #         round, max_round, len(new_tasks), len(links_pool)
    #     ))

    #     new_links = run_downloader_tasks(tasks)
    #     links_pool.append(new_links)

    # step 2, download references of existing papers
    # for ref in new_links:
    #     if 'id' not in ref or 'slug' not in ref:
    #         continue
    #     pid = ref['id']
    #     url = url_ptn % (ref['slug'], pid)

    #     add_to_tasks(tasks, RequestType.REFERENCE, page_url=url, pid=pid)


if __name__ == '__main__':
    main()

import os

from configs import (
    crawler_config,
    PROJECT_ROOT,
)

from configs_pb2.api_spec_pb2 import (
    PaperTask,
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


task_history = set()


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


def url2title(url):
    url = url.strip()
    base_url = url.split('?', 1)[0]
    title = base_url.split('/')[-2]
    title = ' '.join(title.split('-'))
    return title


def get_oupout_filename(pid: str, request_config: RequestConfig):
    local_cache_root = os.path.expanduser(crawler_config.local_cache_root)

    output_dir = os.path.join(local_cache_root, request_config.output_dir)

    # ensure output dir exists
    os.makedirs(output_dir, exist_ok=True)

    return os.path.join(output_dir, '%s.json' % pid)


def add_paper_to_tasks(tasks, pid=None, page_url=None, title=None, skip_exists=True) -> int:
    added_cnt = 0

    if [pid, page_url].count(None) != 1:
        raise ValueError('pid and page_url must be set one')

    if pid is None:
        pid = url2pid(page_url)

    if title is None and page_url is not None:
        title = url2title(page_url)
    assert title is not None, 'title must be set if pid is used'
    # title = title or ''

    paper_task = PaperTask()
    paper_task.pid = pid
    paper_task.title = title

    add_subtask(paper_task, RequestType.CITATION, pid, skip_exists)
    add_subtask(paper_task, RequestType.REFERENCE, pid, skip_exists)

    if len(paper_task.subtasks) > 0:
        tasks.append(paper_task)
        added_cnt += 1

    return added_cnt


def add_subtask(task: PaperTask, request_type: RequestType, pid: str, skip_exists=True) -> int:
    added_cnt = 0

    request_config = None
    for i in conf.request_configs:
        if i.request_type == request_type:
            request_config = i
            break
    if request_config is None:
        raise ValueError('missing request config for %s' % request_type)

    output_file = get_oupout_filename(pid, request_config)
    if skip_exists and output_file in task_history:
        logger.debug('skip existing file: %s' % output_file)
        return added_cnt

    task_history.add(output_file)

    subtask = DownloaderTask()
    subtask.pid = pid
    subtask.task_name = RequestType.Name(request_type).lower()
    subtask.request_config.CopyFrom(request_config)
    subtask.output_file = output_file

    # add subtask to task
    task.subtasks.append(subtask)

    added_cnt += 1
    return added_cnt


def add_to_links_pool(links_pool, links):
    old_cnt = len(links_pool)

    for link in links:
        if len(link) == 1:
            link = link.popitem()[1]

        pid = link['paperId']
        # overwrite if exists
        if pid not in links_pool:
            links_pool[pid] = link
        else:
            links_pool[pid].update(link)

    added_cnt = len(links_pool) - old_cnt
    return added_cnt


def sort_valid_links(links_pool):
    valid_links = []
    drop_stat = {
        'no_fieldsOfStudy': 0,
        'citationCount_lt_10': 0,
        'fieldsOfStudy_not_in': 0,
    }

    sfields = {
        'Computer Science',
    }
    sfields_found = set()

    for pid, link in links_pool.items():
        if pid is None:
            continue

        if not isinstance(link['citationCount'], int):
            drop_stat['citationCount_lt_10'] += 1
            continue

        if link['citationCount'] < 10:
            drop_stat['citationCount_lt_10'] += 1
            continue

        if link.get('fieldsOfStudy') is None:
            drop_stat['no_fieldsOfStudy'] += 1
            continue

        fieldsOfStudy = set(link['fieldsOfStudy'])

        if len(fieldsOfStudy) == 0:
            drop_stat['no_fieldsOfStudy'] += 1
            continue

        sfields_found.update(fieldsOfStudy)
        if len(fieldsOfStudy & sfields) == 0:
            drop_stat['fieldsOfStudy_not_in'] += 1
            continue

        valid_links.append(link)

    logger.info('drop stat: %s' % drop_stat)

    # sort by citationCount
    valid_links.sort(key=lambda x: x['citationCount'], reverse=True)

    # save valid links for debug
    # with open('valid_links.json', 'w') as f:
    #     import json
    #     json.dump(valid_links, f, indent=4)

    return valid_links


def pick_top(yearly_links):
    cnt = len(yearly_links)
    valuable_cnt = min(conf.valuable_paper_yearly, int(cnt * conf.top_paper_ratio))
    valuable_cnt = max(conf.yearly_min_pick_count, valuable_cnt)

    return yearly_links[:valuable_cnt]


def find_valuable_links(valid_links):
    yearly_groups = {}
    for link in valid_links:
        key = int(link['year'] or 1900)
        yearly_groups.setdefault(key, []).append(link)

    valuable_links = []
    other_year_links = []

    # newer first
    yearly_peak = 0
    for year, links in sorted(yearly_groups.items(), key=lambda x: x[0], reverse=True):
        year_cnt = len(links)
        if year_cnt > yearly_peak:
            yearly_peak = year_cnt
        elif year_cnt < yearly_peak * 0.5:
            other_year_links.extend(links)
            continue

        yearly_valuable_links = pick_top(links)
        valuable_links.extend(yearly_valuable_links)

        logger.info('%s, paper count: %s, valuable choose: %s' % (
            year, len(links), len(yearly_valuable_links)))

    other_valuable_links = pick_top(other_year_links)
    valuable_links.extend(other_valuable_links)

    logger.info('%s, paper count: %s, valuable choose: %s' % (
        'other year', len(other_year_links), len(other_valuable_links)))

    return valuable_links


def main():
    seed_urls = load_seed_urls()

    links_pool = {}

    # step 1, download seed_urls ref and citation
    tasks = []
    for url in seed_urls:
        add_paper_to_tasks(tasks, page_url=url, skip_exists=False)

    new_links = run_downloader_tasks(tasks, log_prefix=' of seed_urls.')

    max_round = conf.max_round
    for round in range(1, max_round+1):

        add_to_links_pool(links_pool, new_links)
        valid_links = sort_valid_links(links_pool)
        valuable_links = find_valuable_links(valid_links)

        tasks = []
        for link in valuable_links:
            title = '%s-%s' % (link['year'], link['title'])
            add_paper_to_tasks(tasks, pid=link['paperId'], title=title)
            if len(tasks) >= conf.max_paper_in_round:
                break

        logger.info('=== round %s info === tasks: %s. valuable_links: %s, valid_links: %s, link_pool: %s' % (
            round, len(tasks), len(valuable_links), len(valid_links), len(links_pool)
        ))

        if len(tasks) == 0:
            logger.info('no more tasks, exit.')
            break

        new_links = run_downloader_tasks(tasks, log_prefix=' of round %s/%s.' % (round, max_round))


if __name__ == '__main__':
    main()

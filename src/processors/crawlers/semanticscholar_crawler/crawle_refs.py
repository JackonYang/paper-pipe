import os
import json
from .api import download_ref_links
from configs import (
    CRAWLED_SEMANTIC_SCHOLAR_REF_INFO_DIR as DOWNLOAD_OUTPUT_DIR,
    SEED_REF_MIN_COUNTS,
    DIGGING_REF_MIN_COUNT,
)

import logging

logger = logging.getLogger(__name__)


CUR_DIR = os.path.abspath(os.path.dirname(__file__))

url_ptn = 'https://www.semanticscholar.org/paper/%s/%s?sort=total-citations'


def get_outfile(pid):
    return os.path.join(DOWNLOAD_OUTPUT_DIR, '%s.json' % pid)


def append_url_by_string(urls, url, drop_exists=False):
    url = url.strip()
    base_url = url.split('?', 1)[0]
    pid = base_url.split('/')[-1]

    outfile = get_outfile(pid)
    if drop_exists and os.path.exists(outfile):
        return

    urls.append([pid, url, outfile])


def append_url_by_dict(urls, ref, drop_exists=False):
    if 'id' not in ref or 'slug' not in ref:
        return

    pid = ref['id']
    url = url_ptn % (ref['slug'], pid)

    outfile = get_outfile(pid)
    if drop_exists and os.path.exists(outfile):
        return

    urls.append([pid, url, outfile])


def read_urls_from_file(file_path):
    with open(file_path, 'r') as f:
        data = f.readlines()

    urls = []
    for url in data:
        append_url_by_string(urls, url)
    return urls


def read_urls_from_refs(dir_path):
    urls = []
    for file_path in os.listdir(dir_path):
        if not file_path.endswith('.json'):
            continue
        with open(os.path.join(dir_path, file_path), 'r') as f:
            data = json.load(f)
        for ref in data['links']:
            append_url_by_dict(urls, ref)
    return urls


def download_urls(urls):

    if not os.path.exists(DOWNLOAD_OUTPUT_DIR):
        os.makedirs(DOWNLOAD_OUTPUT_DIR)

    ref_urls = []

    for idx, task in enumerate(urls):
        pid, url, outfile = task

        if os.path.exists(outfile):
            with open(outfile, 'r') as fr:
                data = json.load(fr)
            new_ref_links = data['links']
        else:
            data = download_ref_links(pid, url, outfile)
            new_ref_links = data['links']
            logger.info('(%s/%s)%s refs downloaded. url: %s' % (
                idx + 1, len(urls), len(new_ref_links), url))

        for ref in new_ref_links:
            append_url_by_dict(ref_urls, ref)

    return ref_urls


def filter_valuable_urls(urls, min_count=5, drop_exists=False):
    # count occurence of each url
    url_count = {}
    for task in urls:
        if isinstance(task, str):
            url = task
        else:
            url = task[1]

        if url not in url_count:
            url_count[url] = 0
        url_count[url] += 1

    new_urls = []
    for url in url_count:
        if url_count[url] > min_count:
            append_url_by_string(new_urls, url, drop_exists=drop_exists)
    return new_urls


def download_seed(seed_url):
    ref_min_cnts = SEED_REF_MIN_COUNTS

    urls = [seed_url]
    for idx, ref_min_cnt in enumerate(ref_min_cnts):

        golden_urls = filter_valuable_urls(urls, ref_min_cnt, drop_exists=False)

        logger.info('start seed round: %s, golden url cnt: %s, orig cnt: %s. seed_url: %s' % (idx + 1, len(golden_urls), len(urls), seed_url[1]))

        urls = download_urls(golden_urls)


def main():

    # seeds (paper urls) to crawler
    list_file = os.path.join(CUR_DIR, 'url.list')

    # output dir, downloaded paper reference info saved here
    if not os.path.exists(DOWNLOAD_OUTPUT_DIR):
        os.makedirs(DOWNLOAD_OUTPUT_DIR)

    # counter. used to calc newly downloaded paper ref info count
    orig_ref_file_cnt = len(os.listdir(DOWNLOAD_OUTPUT_DIR))

    # download seeds defined in list_file
    seed_urls = read_urls_from_file(list_file)
    for seed_url in seed_urls:
        download_seed(seed_url)

    digging_round_idx = 1
    digging_ref_min_cnt = DIGGING_REF_MIN_COUNT

    # dig more reference links and download them
    while True:
        urls = read_urls_from_refs(DOWNLOAD_OUTPUT_DIR)

        chosen_urls = filter_valuable_urls(urls, min_count=digging_ref_min_cnt, drop_exists=True)

        if len(chosen_urls) == 0:
            # no more valuable links to download
            break

        logger.info('start digging round: %s, chosen_count: %s, candidate_count: %s' % (digging_round_idx, len(chosen_urls), len(urls)))
        download_urls(chosen_urls)

        digging_round_idx += 1

    new_ref_file_cnt = len(os.listdir(DOWNLOAD_OUTPUT_DIR))

    logger.info('newly download count: %s, total reference file count: %s' % (new_ref_file_cnt - orig_ref_file_cnt, new_ref_file_cnt))


if __name__ == '__main__':
    main()
import os

from configs import (
    crawler_config,
    PROJECT_ROOT,
)

from .downloader import run_downloader
from . import request_citation

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


def main():
    seed_urls = load_seed_urls()

    local_cache_root = os.path.expanduser(crawler_config.local_cache_root)
    out_dir_citation = os.path.join(local_cache_root, conf.citation_configs.output_dir)
    out_dir_ref = os.path.join(local_cache_root, conf.reference_configs.output_dir)

    # ensure output dir exists
    if not os.path.exists(out_dir_citation):
        os.makedirs(out_dir_citation)
    if not os.path.exists(out_dir_ref):
        os.makedirs(out_dir_ref)

    for idx, url in enumerate(seed_urls):
        pid = url2pid(url)
        outfile = os.path.join(out_dir_citation, '%s.json' % pid)

        # step1.1, download seed's citations
        data = run_downloader(pid, url, request_citation.send_request, conf.citation_configs, outfile)

        msg = '(%s/%s) %s citations downloaded. url: %s' % (
            idx + 1, len(seed_urls), len(data['links']), url)
        logger.info(msg)


if __name__ == '__main__':
    main()

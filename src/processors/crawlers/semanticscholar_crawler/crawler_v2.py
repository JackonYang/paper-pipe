import os

from configs import (
    crawler_config,
    PROJECT_ROOT,
)

conf = crawler_config.semantic_scholar_config


def load_seed_urls():
    seed_file = os.path.join(PROJECT_ROOT, conf.seed_file)

    with open(seed_file, 'r') as f:
        data = f.readlines()

    return [i.strip() for i in data if i.strip()]


def main():
    seed_urls = load_seed_urls()
    print('---')
    print('\n'.join(seed_urls))


if __name__ == '__main__':
    main()

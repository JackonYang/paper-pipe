import os

import logging

logger = logging.getLogger(__name__)


class BasePipeline(object):
    """Base Pipeline Definition for PaperPipe"""
    pipe_name = None

    def run_all(self, **kwargs):
        logger.info('running %s.run_all()' % self.__class__.__name__)

        ret = 0
        assert isinstance(ret, int), 'exit code requires <int>'
        return ret

    def console_output(self, msg):
        print('\033[1;36m{0}\033[0m'.format(msg))


# === util functions ===


def should_skip_func(func_name):
    env_var_name = 'SKIP_%s' % func_name.upper()

    return os.environ.get(env_var_name, 'FALSE').upper() == 'TRUE'

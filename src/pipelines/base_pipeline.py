import os

import logging

logger = logging.getLogger(__name__)


class BasePipeline(object):
    """Base Pipeline Definition for PaperPipe"""
    pipe_name = None

    pre_run_steps = [
    ]

    post_run_steps = [
    ]

    def run(self, **kwargs):
        raise NotImplementedError

    def run_all(self, **kwargs):
        logger.info('running %s.run_all()' % self.__class__.__name__)

        # pre run
        self.run_step_group('pre_run', self.pre_run_steps, **kwargs)

        ret = self.run(**kwargs)

        # post run
        self.run_step_group('post_run', self.post_run_steps, **kwargs)

        ret = 0
        assert isinstance(ret, int), 'exit code requires <int>'
        return ret

    def run_step_group(self, group_name, steps, stop_on_fail=False, **kwargs):
        ret = 0

        for name, func in steps:
            if should_skip_func(name):
                msg = 'skip running %s step' % name
                self.console_output(msg)
                continue

            # func is a string, which is the name of the function
            if not callable(func):
                func = getattr(self, func)

            # run func
            logger.debug('step running: %s, group name: %s' % (name, group_name))
            ret = func(**kwargs)
            if stop_on_fail and ret != 0:
                msg = 'step %s failed. ret: %s, exit' % (name, ret)
                self.console_output(msg)
                return ret

        return ret

    def console_output(self, msg):
        logger.info(msg)
        print('\033[1;36m{0}\033[0m'.format(msg))


# === util functions ===


def should_skip_func(func_name):
    env_var_name = 'SKIP_%s' % func_name.upper()

    return os.environ.get(env_var_name, 'FALSE').upper() == 'TRUE'

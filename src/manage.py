import sys
import argparse
import os
import json
from importlib import import_module
import configs  # noqa E402. enable logging


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
pipeline_dirname = 'pipelines'

ignored_pipe_names = [
    '__init__.py',
    'base_pipeline.py',
]

pipeline_choices = [
    f[:-3].replace('_', '-') for f in os.listdir(os.path.join(CURRENT_DIR, pipeline_dirname)) if f.endswith('.py') and f not in ignored_pipe_names
]

# use to manually skip some steps by setting env var skip_*
sub_steps = [
    'gen_note_from_pdf',
    'gen_note_from_ref',
]


def default_pipe_runner_func(**kwargs):
    print('pipe runner is not defined. user args: %s' % json.dumps(kwargs, indent=4))
    return 1


def load_pipeline_runner(pipe_name):

    module_name = '%s.%s' % (
        pipeline_dirname, pipe_name.replace('-', '_'))
    pipe_module = import_module(module_name)

    func = pipe_module.pipe_runner_func
    # func = default_pipe_runner_func

    return func


def load_ini():
    raise NotImplementedError


def init_argparser():
    parser = argparse.ArgumentParser(description='Commond Line Interface for PaperPipe.')

    parser.add_argument(
        'pipeline', metavar='pipeline', type=str,
        help=', '.join(pipeline_choices))

    parser.add_argument(
        '--ini', metavar='job_params', type=str,
        default=None,
        help='path to your job_config.ini file')

    for step in sub_steps:
        key = 'skip_%s' % step.replace('-', '_')
        name = '--%s' % key.replace('_', '-')
        parser.add_argument(
            name, dest=key, action='store_true', default=False)

    return parser


def run_pipeline(pipeline, kwargs):
    pipe_runner_func = load_pipeline_runner(pipeline)
    err_no = pipe_runner_func(**kwargs)

    if err_no is None:
        raise ValueError('missing return code. pipeline: %s, runner function: %s, file: %s' %
                         (pipeline, pipe_runner_func.__name__, pipe_runner_func.__code__.co_filename))

    return err_no


def run_job(args):
    err_no = 0

    # init pipeline runner
    pipeline = args.pipeline

    # init kwargs dict
    if args.ini and os.path.exists(args.ini):
        kwargs = load_ini(args.ini)
    else:
        kwargs = vars(args)

    # print(kwargs)
    # update kwargs if specified in command line args
    # save args.skip_* to kwargs
    # for step in sub_steps:
    #     key = 'skip_%s' % step.replace('-', '_')
    #     kwargs[key] = getattr(args, key)

    # run the pipeline
    err_no = run_pipeline(pipeline, kwargs)
    return err_no


def main():
    parser = init_argparser()
    args = parser.parse_args()

    err_no = run_job(args)
    return err_no


if __name__ == '__main__':
    err_no = main()
    sys.exit(err_no)

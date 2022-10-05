from manage import run_pipeline


def iter_pipe(pipelines):
    for i in pipelines:
        if isinstance(i, str):
            yield i, {}
        yield i


def test_pipelines():
    pipelines = [
        [
            'gen-notes-md',
            {
                'skip_gen_note_from_ref': True,

            },
        ],
    ]

    for pipeline, pipe_kwargs in iter_pipe(pipelines):
        err_no = run_pipeline(pipeline, pipe_kwargs)
        assert err_no == 0, 'pipeline %s failed' % pipeline

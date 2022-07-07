from .base_pipeline import BasePipeline


class GenNotesMdPipe(BasePipeline):
    pass


pipe_runner_func = GenNotesMdPipe().run_all

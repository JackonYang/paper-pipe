from .base_pipeline import BasePipeline


class GenPdfMetaPipe(BasePipeline):
    pass


pipe_runner_func = GenPdfMetaPipe().run_all

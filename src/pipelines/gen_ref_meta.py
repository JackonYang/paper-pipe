from .base_pipeline import BasePipeline

from processors.crawlers.semanticscholar_crawler.collect_ref_meta import main as run_semanticscholar_gen_ref_meta

import logging

logger = logging.getLogger(__name__)


class CollectRefMetaPipe(BasePipeline):

    def run(self, **kwargs):
        # semantic scholar
        run_semanticscholar_gen_ref_meta()


pipe_runner_func = CollectRefMetaPipe().run_all

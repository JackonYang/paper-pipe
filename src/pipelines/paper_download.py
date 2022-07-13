from .base_pipeline import BasePipeline

from processors.crawlers.semanticscholar_crawler.crawle import main as run_semanticscholar_crawler

import logging

logger = logging.getLogger(__name__)


class PaperDownloadPipe(BasePipeline):

    def run(self, **kwargs):
        logger.info('start download papers')
        run_semanticscholar_crawler()


pipe_runner_func = PaperDownloadPipe().run_all

from typing import Optional

from indexer.crawl_result import CrawlResult
from indexer.database_connection import DatabaseConnectionParameters
from indexer.indexer import Indexer
from indexer.indexer_type import IndexerType
from indexer.language import Language
from indexer.rabbitmq_connection import RabbitMQConnectionParameters

"""
    Usage example
"""

if __name__ == '__main__':
    class GitLabIndexer(Indexer):
        def crawl_next_repository(self, prev_repository_id: Optional[str]) -> CrawlResult:
            return CrawlResult(
                               str(
                                   int(prev_repository_id if prev_repository_id is not None else 7)+1
                               ),
                               "https://url",
                               "git://url",
                               {
                                   Language.C: True,
                                   Language.CPP: False,
                                   Language.CSHARP: False,
                                   Language.CSS: True,
                                   Language.JAVA: True,
                                   Language.JS: False,
                                   Language.PHP: False,
                                   Language.Python: False,
                                   Language.Ruby: True
                                }
                               )

    rabbit = RabbitMQConnectionParameters("172.17.0.2")
    database = DatabaseConnectionParameters("172.17.0.3", "frege", "postgres", "password")

    app = GitLabIndexer(IndexerType.GITLAB, rabbit, database, 10)

    app.run()

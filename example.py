from typing import Optional

from fregeindexerlib.crawl_result import CrawlResult
from fregeindexerlib.database_connection import DatabaseConnectionParameters
from fregeindexerlib.indexer import Indexer
from fregeindexerlib.indexer_type import IndexerType
from fregeindexerlib.language import Language
from fregeindexerlib.rabbitmq_connection import RabbitMQConnectionParameters

"""
    Usage example
"""

if __name__ == '__main__':
    class GitLabIndexer(Indexer):
        def crawl_next_repository(self, prev_repository_id: Optional[str]) -> Optional[CrawlResult]:
            if prev_repository_id is not None and prev_repository_id == 30:
                return None
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

    rabbit = RabbitMQConnectionParameters(host="172.17.0.2")
    database = DatabaseConnectionParameters(host="172.17.0.3", database="frege",
                                            username="postgres", password="password")

    app = GitLabIndexer(indexer_type=IndexerType.GITLAB, rabbitmq_parameters=rabbit,
                        database_parameters=database, rejected_publish_delay=10)

    app.run()

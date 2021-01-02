from datetime import datetime
from typing import Optional

from sqlalchemy import TIMESTAMP, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Sequence, ForeignKey

from fregeindexerlib.crawl_result import CrawlResult
from fregeindexerlib.database_connection import DatabaseConnectionParameters
from fregeindexerlib.indexer_type import IndexerType
from fregeindexerlib.language import Language


Base = declarative_base()


class RepositoriesTable(Base):
    __tablename__ = "repositories"
    repo_id = Column(String, primary_key=True)
    git_url = Column(String)
    repo_url = Column(String)
    crawl_time = Column(TIMESTAMP(timezone=True))
    download_time = Column(TIMESTAMP(timezone=True))
    commit_hash = Column(String)


class RepositoryLanguageTable(Base):
    __tablename__ = "repository_language"
    id = Column(Integer, Sequence('repository_language_id_seq'), primary_key=True)
    repository_id = Column(String, ForeignKey('repositories.repo_id'))
    language_id = Column(Integer)
    present = Column(Boolean)
    analyzed = Column(Boolean)


class Database:
    def __init__(self, database_parameters: DatabaseConnectionParameters, indexer_type: IndexerType):
        self.database_parameters = database_parameters
        self.engine = create_engine(f'postgresql://{self.database_parameters.username}:'
                                    f'{self.database_parameters.password}@{self.database_parameters.host}:'
                                    f'{self.database_parameters.port}/{self.database_parameters.database}')
        self.indexer_type = indexer_type
        self.connection = None

    def connect(self):
        self.connection = self.engine.connect()
        self.IndexerTable = self._get_indexer_table()
        self.IndexerTable.__table__.create(bind=self.connection, checkfirst=True)

        self.Session = sessionmaker(bind=self.connection)
        session = self.Session()
        if session.query(self.IndexerTable).count() < 1:
            row = self.IndexerTable(id=1, last_crawled_id="")
            session.add(row)
        session.commit()

    def save_last_crawled_id(self, last_crawled_id: str):
        session = self.Session()
        session.query(self.IndexerTable).filter_by(id=1).first().last_crawled_id = last_crawled_id
        session.commit()

    def get_last_crawled_id(self) -> Optional[str]:
        session = self.Session()
        last_crawled_id = session.query(self.IndexerTable).filter_by(id=1).first().last_crawled_id
        session.commit()
        return last_crawled_id if last_crawled_id != "" else None

    def save_crawl_result(self, crawl_result: CrawlResult, generated_repo_id: str):
        session = self.Session()
        repository_row = RepositoriesTable(repo_id=generated_repo_id, git_url=crawl_result.git_url,
                                           repo_url=crawl_result.repo_url, crawl_time=datetime.now(),
                                           download_time=None, commit_hash=None)
        session.add(repository_row)
        session.flush()

        if crawl_result.languages is not None:
            for lang in Language:
                lang_row = RepositoryLanguageTable(repository_id=generated_repo_id, language_id=lang.value,
                                                   present=crawl_result.languages.get(lang, False), analyzed=False)
                session.add(lang_row)

        session.commit()

    def _get_indexer_table(self):

        class IndexerTable(Base):
            __tablename__ = self.indexer_type.value['database_table']
            __table_args__ = {'extend_existing': True}
            id = Column(Integer, primary_key=True)
            last_crawled_id = Column(String)

        return IndexerTable

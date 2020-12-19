from abc import ABC, abstractmethod
import logging
from typing import Optional

import pika
import json
import sys
import time

from sqlalchemy import exc

from indexer.crawl_result import CrawlResult
from indexer.database import Database
from indexer.database_connection import DatabaseConnectionParameters
from indexer.indexer_type import IndexerType
from indexer.rabbitmq_connection import RabbitMQConnectionParameters


class Indexer(ABC):
    QUEUE_NAME = "download"

    def __init__(self, indexer_type: IndexerType, rabbitmq_parameters: RabbitMQConnectionParameters,
                 database_parameters: DatabaseConnectionParameters, rejected_publish_delay: int):
        self.indexer_type = indexer_type
        self.rabbitmq_parameters = rabbitmq_parameters
        self.database_parameters = database_parameters
        self.rejected_publish_delay = rejected_publish_delay
        self.log = logging.getLogger("Indexer")
        self.log.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        self.log.addHandler(handler)

    def run(self):
        database = Database(self.database_parameters, self.indexer_type)

        while True:
            try:
                rmq_connection, channel = self._connect_to_rabbitmq()
                self._connect_to_database(database)
                while True:
                    message_to_sent = True

                    last_crawled_id = database.get_last_crawled_id()

                    self.before_crawl(last_crawled_id)

                    crawl_result = self.crawl_next_repository(last_crawled_id)

                    self.after_crawl(crawl_result)

                    payload = self._prepare_downloader_message(crawl_result)

                    while message_to_sent:
                        try:
                            channel.basic_publish(exchange='',
                                                  routing_key=self.QUEUE_NAME,
                                                  properties=pika.BasicProperties(
                                                      delivery_mode=2,  # make message persistent
                                                  ),
                                                  body=payload)
                            self.log.debug("Message was received by RabbitMQ")

                            database.save_crawl_result(crawl_result, self._create_repo_id(crawl_result.id))
                            self.log.debug("Crawl result saved into database")

                            database.save_last_crawled_id(crawl_result.id)
                            self.log.debug("Last crawled id saved into database")

                            self.on_successful_process(crawl_result)

                            message_to_sent = False
                        except pika.exceptions.NackError:
                            self.log.debug(f"Message was REJECTED by RabbitMQ (queue full?). "
                                           f"Retrying in {self.rejected_publish_delay}s")
                            time.sleep(self.rejected_publish_delay)

            except pika.exceptions.AMQPConnectionError as exception:
                self.log.error(f"AMQP Connection Error: {exception}")
                self.log.info("Reconnecting to RabbitMQ and database")
                self.on_error(exception)
            except exc.DBAPIError as exception:
                self.log.error(f"Database connection error: {exception}")
                self.log.info("Reconnecting to RabbitMQ and database")
                self.on_error(exception)
            except KeyboardInterrupt:
                self.log.info(" Exiting...")
                try:
                    rmq_connection.close()
                except NameError:
                    pass
                sys.exit(0)

    def _connect_to_rabbitmq(self):
        while True:
            try:
                self.log.info(f"Connecting to RabbitMQ ({self.rabbitmq_parameters.host}:"
                              f"{self.rabbitmq_parameters.port})...")
                rmq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_parameters.host,
                                                                                   port=self.rabbitmq_parameters.port))
                channel = rmq_connection.channel()
                self.log.info("Connected to RabbitMQ")
                channel.confirm_delivery()
                channel.queue_declare(queue=self.QUEUE_NAME, durable=True)
                return rmq_connection, channel
            except pika.exceptions.AMQPConnectionError as exception:
                self.log.error(f"AMQP Connection Error: {exception}")
                time.sleep(5)

    def _connect_to_database(self, database: Database):
        while True:
            try:
                self.log.info("Connecting to a database")
                database.connect()
                self.log.info("Connected to a database")
                return
            except exc.DBAPIError as exception:
                self.log.error(f"Database connection error: {exception}")
                time.sleep(5)
                if not exception.connection_invalidated:
                    raise exception

    def _prepare_downloader_message(self, crawl_result: CrawlResult) -> bytes:
        message = {
            "repo_id": self._create_repo_id(crawl_result.id),
            "git_url": crawl_result.git_url
        }
        if crawl_result.languages is not None:
            message['languages'] = [language.value for language in crawl_result.languages.keys()]

        return bytes(json.dumps(message), encoding='utf-8')

    def _create_repo_id(self, crawled_id: str):
        return f"{self.indexer_type.value['id_prefix']}_{crawled_id}"

    @abstractmethod
    def crawl_next_repository(self, prev_repository_id: Optional[str]) -> CrawlResult:
        """
        Method responsible for crawl a next repository
        :param prev_repository_id: last crawled repository ID (returned by API and passed to a CrawlResult) - might
            be None if there was not previously crawled repositories
        :return: filled CrawlResult
        """
        pass

    def after_crawl(self, crawl_result: CrawlResult):
        pass

    def before_crawl(self, prev_repository_id: Optional[str]):
        pass

    def on_successful_process(self, crawl_result: CrawlResult):
        pass

    def on_error(self, exception: Exception):
        pass

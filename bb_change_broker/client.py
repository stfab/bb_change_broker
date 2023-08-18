"""Client that sends changes from change source to RabbitMQ."""

import time, threading

from bb_change_broker.change_source.git import GitChangeSource
from bb_change_broker.change_source.svn import SubversionChangeSource
from bb_change_broker.publisher.broker import BrokerPublisher
from bb_change_broker.publisher.buildbot import BuildbotPublisher
from bb_change_broker.util.log import Logger


class Client:
    """Client that sends changes from change source to RabbitMQ."""

    def __init__(self, config):
        """Initialize the client.

        :param config (dict): The configuration of the client.
        """
        self.logger = Logger(
            config["DEFAULT"]["log_file"] if "log_file" in config["DEFAULT"] else None,
            int(config["DEFAULT"]["log_level"])
            if "log_level" in config["DEFAULT"]
            else 10,
        )
        self.rabbitmq = BrokerPublisher(
            host=config["rabbitmq"]["host"],
            port=int(config["rabbitmq"]["port"]),
            username=config["rabbitmq"]["username"],
            password=config["rabbitmq"]["password"],
            logger=self.logger,
        )
        self.buildbot = BuildbotPublisher(
            host=config["buildbot"]["host"],
            port=int(config["buildbot"]["port"]),
            username=config["buildbot"]["username"],
            password=config["buildbot"]["password"],
            encoding=config["DEFAULT"]["encoding"],
            logger=self.logger,
        )

        if "git" in config:
            self.change_source = GitChangeSource(
                repository=config["git"]["repository"],
                logger=self.logger,
                encoding=config["DEFAULT"]["encoding"],
            )
        elif config["svn"] != None:
            self.change_source = SubversionChangeSource(
                repository=config["svn"]["repository"],
                filters=config["svn"]["branch_filters"],
                logger=self.logger,
                encoding=config["DEFAULT"]["encoding"],
            )
        self.queue = config["rabbitmq"]["queue"]

    def run(self):
        """Run the client."""
        changes = self.change_source.get_changes()
        for change in changes:
            if not (
                self.rabbitmq.publish(str(change), exchange="", routing_key=self.queue)
                # TODO: For each buildbot we need a queue or we send multiple messages to the same queue
                # with some identifier for the buildbot
            ):
                self.logger.error(
                    "Failed to publish change to RabbitMQ, sending to Buildbot instead."
                )
                thread = threading.Thread(
                    target=self.__buildbot_publish, args=(change, self.buildbot, 5, 1)
                )
                thread.start()

    def __buildbot_publish(self, change, buildbot, retry_timeout=5, max_retries=1):
        """Publish a change to a Buildbot.

        :param change (Change): The change to publish.
        :param buildbot (BuildbotPublisher): The Buildbot to publish to.
        :param retry_timeout (int): The timeout in seconds to wait before retrying.
        :param max_retries (int): The maximum number of retries.
        """
        retry_counter = 0
        while retry_counter < max_retries:
            if buildbot.publish(change):
                return
            self.logger.error(
                "Failed to publish change to Buildbot %s, waiting %s seconds and trying again."
                % (buildbot.host, retry_timeout)
            )
            time.sleep(retry_timeout)
            retry_counter += 1
        self.logger.error(
            "Failed to publish change to Buildbot %s, exiting." % buildbot.host
        )

"""Server that consumes changes from broker and publishs them to buildbot."""

import threading

from bb_change_broker.publisher.buildbot import BuildbotPublisher
from bb_change_broker.consumer.broker import BrokerConsumer
from bb_change_broker.util.log import Logger


class Server(object):
    """Server that consumes changes from broker and publishs them to buildbot."""

    def __init__(self, config):
        """Initialize the server.

        :param config (dict): The configuration of the server.
        """
        self.logger = Logger(config["logging"] if "logging" in config else None)
        self.rabbitmq = BrokerConsumer(
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
        self.queue = config["rabbitmq"]["queue"]

    def callback(self, ch, method, properties, body):
        """Callback function that is called when a message is received from broker.

        :param ch (pika.channel.Channel): The channel of the message.
        :param method (pika.spec.Basic.Deliver): The method of the message.
        :param properties (pika.spec.BasicProperties): The properties of the message.
        :param body (str): The body of the message.
        """
        self.logger.info("Received message %r" % body)
        if self.buildbot.is_available() and self.buildbot.publish(eval(body)):
            self.logger.debug("Sent to buildbot")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            self.logger.error("Failed to send to buildbot")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def run(self):
        """Run the server."""
        thread = threading.Thread(
            target=self.rabbitmq.consume, args=(self.queue, self.callback)
        )
        thread.start()

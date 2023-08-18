"""Module for broker publisher class."""

from bb_change_broker.publisher.base import BasePublisher
from bb_change_broker.backend.broker import PikaHandler
from bb_change_broker.util.log import Logger


class BrokerPublisher(BasePublisher):
    """Publisher class that sends changes to broker."""

    def __init__(
        self, host, port, username, password, handler=PikaHandler(), logger=Logger()
    ):
        """Initialize the broker publisher.

        :param host (str): The host of the broker.
        :param port (int): The port of the broker.
        :param username (str): The username of the broker.
        :param password (str): The password of the broker.
        :param handler (BaseBrokerHandler): The handler for the broker.
        :param logger (Logger): The logger to use.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.handler = handler
        self.logger = logger

    def connect(self):
        """Connect to broker.

        :return (pika.BlockingConnection): The connection to broker.
        """
        self.logger.info(
            "Connecting to broker (%s, %s) with user %s ...",
            self.host,
            self.port,
            self.username,
        )
        credentials = self.handler.credentials(self.username, self.password)
        parameters = self.handler.connection_parameters(
            self.host, self.port, "/", credentials
        )
        connection = self.handler.blocking_connection(parameters)
        return connection

    def close(self):
        """Close the connection to broker."""
        pass

    def publish(self, message, exchange, routing_key) -> bool:
        """Publish a message to broker.

        :param message (str): The message to publish.
        :param exchange (str): The exchange to publish the message to.
        :param routing_key (str): The routing key to publish the message with.
        :return (bool): True if the message was published successfully, False otherwise.
        """
        try:
            connection = self.connect()
            channel = connection.channel()
            self.logger.info(
                "Publishing message to queue %s ...",
                routing_key,
            )
            channel.queue_declare(queue=routing_key, durable=True)
            self.logger.debug("Send message: %s", message)
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message,
                properties=channel.get_properties(delivery_mode=2),
            )
            connection.close()
            self.logger.debug("Message published successfully, closing connection.")
            return True
        except Exception as e:
            self.logger.error("Failed to publish message")
            self.logger.stack_trace(e)
            return False

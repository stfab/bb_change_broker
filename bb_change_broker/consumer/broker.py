"""Module for consuming messages from broker."""

import time

from bb_change_broker.consumer.base import BaseConsumer
from bb_change_broker.backend.broker import (
    BaseBrokerConnection,
    PikaHandler,
)
from bb_change_broker.util.log import Logger


class BrokerConsumer(BaseConsumer):
    """Consumer class that receives messages from broker."""

    def __init__(
        self,
        host,
        port,
        username,
        password,
        retry_on_disconnect=True,
        handler=PikaHandler(),
        logger=Logger(),
    ):
        """Initialize the broker consumer.

        :param host (str): The host of the the broker.
        :param port (int): The port of the the broker.
        :param username (str): The username of the the broker.
        :param password (str): The password of the the broker.
        :param retry_on_disconnect (bool): Whether to retry on disconnect.
            Note: This flag is only used when testing, because we need to exit the loop.
        :param handler (BaseBrokerHandler): The handler for the broker.
        :param logger (Logger): The logger to use.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.retry_on_disconnect = retry_on_disconnect
        self.handler = handler
        self.logger = logger

    def connect(self) -> BaseBrokerConnection:
        """Connect to broker.

        :return (BaseBrokerChannel): The connection to RabbitMQ.
        """
        credentials = self.handler.credentials(self.username, self.password)
        parameters = self.handler.connection_parameters(
            self.host, self.port, "/", credentials
        )
        connection = self.handler.blocking_connection(parameters)
        return connection

    def close(self):
        """Close the connection to broker."""
        pass

    def consume(self, queue, callback):
        """Consume messages from broker.

        :param queue (str): The queue to consume messages from.
        :param callback (function): The callback function to call when a message is received.
        """

        retries = 0
        while True:
            try:
                connection = self.connect()
                channel = connection.channel()
                # set retry to 0 when connection is successful
                retries = 0
                channel.basic_consume(queue, callback)
                channel.start_consuming()
            except Exception as e:
                self.logger.stack_trace(e)
                if not self.retry_on_disconnect:
                    self.logger.error("Connection closed by broker, exiting")
                    break
                retries += 1
                wait_time = min(2**retries, 30)
                self.logger.warning(
                    "Connection closed by broker, reconnecting in %d seconds"
                    % wait_time
                )
                time.sleep(wait_time)
                continue

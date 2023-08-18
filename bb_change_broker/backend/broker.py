"""Module for broker connection."""

import pika
from abc import ABCMeta, abstractmethod


class BaseBrokerHandler(metaclass=ABCMeta):
    """Abstract class for broker handler."""

    @abstractmethod
    def credentials(self, username, password):
        """Return credentials for broker connection."""
        pass

    def connection_parameters(self, host, port, credentials):
        """Return connection parameters for broker connection.

        :param host (str): The host of the broker.
        :param port (int): The port of the broker.
        :param credentials (pika.PlainCredentials): The credentials for the broker connection.
        """
        pass

    def blocking_connection(self, connection_parameters):
        """Return blocking connection for broker connection.

        :param connection_parameters (pika.ConnectionParameters): The connection parameters for the broker connection.
        """
        pass


class BaseBrokerConnection(metaclass=ABCMeta):
    """Abstract class for broker connection."""

    @abstractmethod
    def channel(self):
        """Return channel for broker connection."""
        pass

    @abstractmethod
    def close(self):
        """Close the connection to broker."""
        pass


class BaseBrokerChannel(metaclass=ABCMeta):
    """Abstract class for broker channel."""

    @abstractmethod
    def queue_declare(self, queue, durable):
        """Declare queue for broker channel.

        :param queue (str): The queue to declare.
        :param durable (bool): Whether the queue should be durable or not.
        """
        pass

    @abstractmethod
    def basic_publish(self, exchange, routing_key, body, properties):
        """Publish a message to broker.

        :param exchange (str): The exchange to publish the message to.
        :param routing_key (str): The routing key to publish the message with.
        :param body (str): The message to publish.
        :param properties (pika.BasicProperties): The properties for the message.
        """
        pass

    @abstractmethod
    def start_consuming(self):
        """Start consuming messages from broker."""
        pass

    @abstractmethod
    def basic_consume(self, queue, callback):
        """Consume messages from broker.

        :param queue (str): The queue to consume messages from.
        :param callback (function): The callback function to call when a message is consumed.
        """
        pass

    @abstractmethod
    def get_properties(self, delivery_mode):
        """Return properties for message.

        :param delivery_mode (int): The delivery mode for the message.
        """
        pass


class PikaHandler(BaseBrokerHandler):
    """Class for broker handler."""

    def credentials(self, username, password):
        """Return credentials for broker connection."""
        return pika.PlainCredentials(username, password)

    def connection_parameters(self, host, port, virtual_host, credentials):
        """Return connection parameters for broker connection."""
        return pika.ConnectionParameters(host, port, virtual_host, credentials)

    def blocking_connection(self, connection_parameters):
        """Return blocking connection for broker connection."""
        return PikaConnection(connection_parameters)


class PikaConnection(BaseBrokerConnection):
    """Class for broker connection."""

    def __init__(self, connection_parameters):
        """Initialize the RabbitMQ connection.

        :param connection_parameters (pika.ConnectionParameters): The connection parameters for the broker connection.
        """
        self.connection = pika.BlockingConnection(connection_parameters)

    def channel(self):
        """Return channel for broker connection.

        :return (DefaultBrokerChannel): The channel for broker connection.
        """
        return PikaChannel(self.connection)

    def close(self):
        """Close the connection to broker."""
        self.connection.close()


class PikaChannel(BaseBrokerChannel):
    """Class for broker channel."""

    def __init__(self, connection):
        """Initialize the RabbitMQ channel.

        :param connection (pika.BlockingConnection): The connection to broker.
        """
        self.channel = connection.channel()

    def queue_declare(self, queue, durable):
        """Declare queue for broker channel.

        :param queue (str): The queue to declare.
        :param durable (bool): Whether the queue is durable or not.
        """
        self.channel.queue_declare(queue, durable=durable)

    def basic_publish(self, exchange, routing_key, body, properties):
        """Publish a message to broker.

        :param exchange (str): The exchange to publish the message to.
        :param routing_key (str): The routing key to publish the message with.
        :param body (str): The message to publish.
        :param properties (pika.BasicProperties): The properties of the message.
        """
        self.channel.basic_publish(exchange, routing_key, body, properties)

    def start_consuming(self):
        """Start consuming messages from broker."""
        self.channel.start_consuming()

    def basic_consume(self, queue, callback):
        """Set up consumer for broker channel.

        :param queue (str): The queue to consume messages from.
        :param callback (function): The callback function to call when a message is received.
        """
        self.channel.basic_consume(queue, callback)

    def get_properties(self, delivery_mode):
        """Get broker properties.

        :param delivery_mode (int): The delivery mode of the message.
        """
        return pika.BasicProperties(delivery_mode=delivery_mode)

from bb_change_broker.backend.broker import (
    BaseBrokerChannel,
    BaseBrokerConnection,
    BaseBrokerHandler,
)


class MockBrokerHandler(BaseBrokerHandler):
    """Class for broker handler."""

    def __init__(self):
        self.connection = None

    def credentials(self, username, password):
        """Return credentials for broker connection."""
        return None

    def connection_parameters(self, host, port, virtual_host, credentials):
        """Return connection parameters for broker connection."""
        return None

    def blocking_connection(self, connection_parameters):
        """Return blocking connection for broker connection."""
        if self.connection is None:
            self.connection = MockConnection(connection_parameters)
        return self.connection


class MockConnection(BaseBrokerConnection):
    """Class for broker connection."""

    def __init__(self, connection_parameters):
        """Initialize the RabbitMQ connection.

        :param connection_parameters (pika.ConnectionParameters): The connection parameters for the broker connection.
        """
        self.ch = None

    def channel(self):
        """Return channel for broker connection.

        :return (DefaultBrokerChannel): The channel for broker connection.
        """
        if self.ch is None:
            self.ch = MockChannel("")
        return self.ch

    def close(self):
        """Close the connection to broker."""
        pass


class MockChannel(BaseBrokerChannel):
    def __init__(self, connection):
        """Initialize the RabbitMQ channel.

        :param connection (pika.BlockingConnection): The connection to broker.
        """
        self.queue = {}
        self.callback = None
        self.queue_name = None

    def queue_declare(self, queue, durable):
        """Declare queue for broker channel.

        :param queue (str): The queue to declare.
        :param durable (bool): Whether the queue is durable or not.
        """
        if queue not in self.queue:
            self.queue[queue] = []

    def basic_publish(self, exchange, routing_key, body, properties):
        """Publish a message to broker.

        :param exchange (str): The exchange to publish the message to.
        :param routing_key (str): The routing key to publish the message with.
        :param body (str): The message to publish.
        :param properties (pika.BasicProperties): The properties of the message.
        """
        self.queue[routing_key].append(body)

    def start_consuming(self):
        """Start consuming messages from broker.

        Note: This is synchronous; the real broker is asynchronous.

        :param queue (str): The queue to consume messages from.
        :param callback (function): The callback function to call when a message is received.
        """
        for message in self.queue[self.queue_name]:
            self.callback(message)
        self.queue[self.queue_name] = []
        # raise exception to simulate disconnect, because consumer won't stop consuming
        raise Exception("Disconnect")

    def basic_consume(self, queue, callback):
        """Consume messages from broker.

        :param queue (str): The queue to consume messages from.
        :param callback (function): The callback function to call when a message is received.
        """
        self.callback = callback
        self.queue_name = queue

    def get_properties(self, delivery_mode):
        """Get broker properties.

        :param delivery_mode (int): The delivery mode of the message.
        """
        return None

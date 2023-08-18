"""Base class for message broker consumers."""


class BaseConsumer:
    """Base class for message broker consumers."""

    def connect(self):
        """Connect to the message broker."""
        raise NotImplementedError

    def close(self):
        """Close the connection to the message broker."""
        raise NotImplementedError

    def consume(self, callback):
        """Consume messages and trigger a callback.

        :param callback (function): The callback function to call when a message is received.
        """
        raise NotImplementedError

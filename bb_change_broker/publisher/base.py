"""Base publisher class."""

from abc import ABCMeta, abstractmethod


class BasePublisher(object, metaclass=ABCMeta):
    """Base publisher class."""

    @abstractmethod
    def connect(self):
        """Connect to the server."""
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """Close the connection to the server."""
        raise NotImplementedError

    @abstractmethod
    def publish(self, message):
        """Publish a message to the server.

        :param message (str): The message to publish.
        """
        raise NotImplementedError

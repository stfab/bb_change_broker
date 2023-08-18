"""Base class for change sources."""

from abc import ABCMeta, abstractmethod


class BaseChangeSource(object, metaclass=ABCMeta):
    """Abstract base class for change sources.

    Change sources are responsible for getting changes from a source and
    returning them as a list of changes.
    """

    @abstractmethod
    def get_changes(self) -> list:
        """Get changes from the change source.

        :return (list): A list of changes.
        """
        raise NotImplementedError

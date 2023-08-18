"""Buildbot sender class that sends changes to buildbot."""

from bb_change_broker.publisher.base import BasePublisher
from bb_change_broker.backend.http_handler import DefaultHTTPHandler
from bb_change_broker.util.log import Logger


class BuildbotPublisher(BasePublisher):
    """Buildbot sender class that sends changes to buildbot."""

    # keys that are allowed to be sent to buildbot
    # TODO: Do we even need this anymore?
    ALLOWED_KEYS = [
        "category",
        "project",
        "repository",
        "branch",
        "revision",
        "author",
        "comments",
        "properties",
        "files",
    ]

    def __init__(
        self,
        host,
        port,
        username,
        password,
        encoding="utf-8",
        http_handler=DefaultHTTPHandler(),
        logger=Logger(),
    ) -> None:
        """Initialize the buildbot sender.

        :param host (str): The host of the buildbot server.
        :param port (int): The port of the buildbot server.
        :param username (str): The username of the buildbot server.
        :param password (str): The password of the buildbot server.
        :param encoding (str): The encoding of the buildbot server.
        :param http_handler (HTTP): The sender to use to send the change to buildbot.
        :param logger (Logger): The logger to use.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.encoding = encoding
        self.http_handler = http_handler
        self.logger = logger

    def connect(self):
        """Connect to buildbot."""
        pass

    def close(self):
        """Close the connection to buildbot."""
        pass

    def publish(self, change) -> bool:
        """Send a change to buildbot.

        :param change (dict): The change to send to buildbot.
        :return (bool): True if the change was sent successfully, False otherwise.
        """
        try:
            if isinstance(change, list):
                change = change[0]

            data = self.__apply_filter(self.__decode_dict(change))
            url = "http://" + self.host + ":" + str(self.port) + "/change_hook/base"
            self.logger.info("Sending %r to %s" % (data, url))
            resp = self.http_handler.post(
                data=data,
                url=url,
                encoding=self.encoding,
                username=self.username,
                password=self.password,
            )
            return True if resp.status == 200 else False
        except Exception as e:
            self.logger.stack_trace(e)
            return False

    def is_available(self):
        """Check if buildbot is available.

        :return (bool): True if buildbot is available, False otherwise.
        """
        try:
            self.logger.debug("Checking if buildbot is available")
            url = "http://" + self.host + ":" + str(self.port)
            resp = self.http_handler.get(url, self.encoding)
            return True if resp.status == 200 else False
        except Exception as e:
            self.logger.stack_trace(e)
            return False

    def __apply_filter(self, c):
        """Apply the filter to the change dict.

        :param c (dict): The change dict to apply the filter to.
        :return (dict): The change dict with the filter applied.
        """
        return {
            key: c[key] for key in self.ALLOWED_KEYS if key in c and c[key] is not None
        }

    def __decode_dict(self, change) -> dict:
        """Decode the bytes in the change dict.

        :param change (dict): The change dict to decode.
        :return (dict): The change dict with bytes decoded.
        """
        return {
            key: change[key].decode(self.encoding)
            if isinstance(change[key], bytes)
            else change[key]
            for key in change
        }

from unittest.mock import Mock
from bb_change_broker.backend.http_handler import BaseHTTPHandler


class MockHTTPHandler(BaseHTTPHandler):
    """Mock HTTP handler class that stores the changes."""

    def __init__(self) -> None:
        """Initialize the mock HTTP handler."""
        self.changes = []

    def post(self, data, url, encoding="utf-8", username=None, password=None):
        """Add the data to the changes and return a successful response.
        
        :param data (dict): The data to send.
        :param url (str): The url to send the data to.
        :param encoding (str): The encoding of the data.
        :param username (str): The username to use for basic auth.
        :param password (str): The password to use for basic auth.
        :return (HTTPResponse): The response from the url.
        """
        self.changes.append(data)
        # mock an object that has a property called status and gives back 200
        resp = Mock()
        resp.status = 200
        return resp

    def get(self, url, encoding="utf-8"):
        """Return a successful response."""
        resp = Mock()
        resp.status = 200
        return resp

    def get_post_data(self):
        """Get the changes that were sent."""
        return self.changes

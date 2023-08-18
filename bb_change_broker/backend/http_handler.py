"""HTTP handler to abstract the HTTP calls."""

import json
import urllib.request
from abc import ABCMeta, abstractmethod


class BaseHTTPHandler(object, metaclass=ABCMeta):
    """Base class for HTTP handler classes."""

    @abstractmethod
    def post(self, data, url, encoding="utf-8", username=None, password=None):
        """Send data to a url.

        :param data (dict): The data to send.
        :param url (str): The url to send the data to.
        :param encoding (str): The encoding of the data.
        :param username (str): The username to use for basic auth.
        :param password (str): The password to use for basic auth.
        :return (HTTPResponse): The response from the url.
        """
        pass

    @abstractmethod
    def get(self, url, encoding="utf-8"):
        """Get data from a url.

        :param url (str): The url to get the data from.
        :param encoding (str): The encoding of the data.
        :return (HTTPResponse): The response from the url.
        """
        pass


class DefaultHTTPHandler(BaseHTTPHandler):
    """HTTP handler to abstract the HTTP calls."""

    def post(self, data, url, encoding="utf-8", username=None, password=None):
        """Post data to a url.

        :param data (dict): The data to post.
        :param url (str): The url to post the data to.
        :param encoding (str): The encoding of the data.
        :param username (str): The username to use for basic auth.
        :param password (str): The password to use for basic auth.
        :return (HTTPResponse): The response from the url.
        """
        req = urllib.request.Request(
            url, data=json.dumps([data]).encode(encoding), method="POST"
        )
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, username, password)
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        resp = opener.open(req)
        return resp

    def get(self, url, encoding="utf-8"):
        """Get data from a url.

        :param url (str): The url to get the data from.
        :param encoding (str): The encoding of the data.
        :return (HTTPResponse): The response from the url.
        """
        req = urllib.request.Request(url, method="GET")
        resp = urllib.request.urlopen(req)
        return resp

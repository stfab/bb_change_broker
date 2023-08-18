import unittest, sys, os, json

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mock"))

from mock.http_handler import MockHTTPHandler
from bb_change_broker.publisher.buildbot import BuildbotPublisher


class TestBuildbotPublisher(unittest.TestCase):
    def setUp(self):
        self.http_handler = MockHTTPHandler()
        self.buildbot_publisher = BuildbotPublisher(
            host="localhost",
            port=8010,
            username="user",
            password="password",
            encoding="utf-8",
            http_handler=self.http_handler,
        )

    def test_publish(self):
        changes = [
            {
                "branch": "master",
                "revision": "f5934acec8193597e0ee60e1be99b0c18654a222",
                "repository": "repository",
                "comments": "rewind",
                "author": "dummy",
                "files": ["FILE1.txt", "FILE2.txt"],
            },
            {
                "branch": "master",
                "revision": "83060a21145596e42d985c798c32aa4b581b7b4f",
                "repository": "repository",
                "author": "user",
                "files": ["somefile.txt"],
                "comments": "New Feature",
            },
        ]
        for change in changes:
            self.buildbot_publisher.is_available()
            self.buildbot_publisher.publish(change)
        received_changes = self.http_handler.get_post_data()
        received_changes = sorted(received_changes, key=lambda k: k["revision"])
        changes = sorted(changes, key=lambda k: k["revision"])
        self.assertEqual(
            received_changes,
            changes,
        )

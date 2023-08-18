import unittest, sys, os, json

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mock"))

from mock.broker import MockBrokerHandler
from bb_change_broker.publisher.broker import BrokerPublisher
from bb_change_broker.consumer.broker import BrokerConsumer
from bb_change_broker.util.log import Logger


class TestBrokerPublisher(unittest.TestCase):
    def setUp(self):
        self.broker_handler = MockBrokerHandler()
        self.logger = Logger("", 10)
        self.broker_publisher = BrokerPublisher(
            host="localhost",
            port=8010,
            username="user",
            password="password",
            handler=self.broker_handler,
            logger=self.logger,
        )
        self.broker_consumer = BrokerConsumer(
            host="localhost",
            port=8010,
            username="user",
            password="password",
            retry_on_disconnect=False,
            handler=self.broker_handler,
            logger=self.logger,
        )

    def test_publish(self):
        # generate some changes, publish them, consume the changes and compare them
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
            self.broker_publisher.publish(
                message=change, exchange="", routing_key="MyQueue"
            )
        received_changes = []
        self.broker_consumer.consume(
            queue="MyQueue", callback=lambda x: received_changes.append(self.__callback(x))
        )

        # sort before comparing
        received_changes = sorted(received_changes, key=lambda k: k["revision"])
        changes = sorted(changes, key=lambda k: k["revision"])

        self.assertEqual(
            received_changes,
            changes,
        )

    def __callback(self, message):
        self.logger.info("Received message %s" % message)
        return message

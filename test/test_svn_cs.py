import unittest, sys, os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mock"))

from mock.cli import MockCli
from bb_change_broker.change_source.svn import SubversionChangeSource
from bb_change_broker.util.log import Logger


class TestSubversionChangeSource(unittest.TestCase):
    def setUp(self):
        self.svn_cs1 = SubversionChangeSource(
            "/srv/svn/repository",
            cli=MockCli(),
            filters=[],
            logger=Logger("/data/bb_change_broker.log", 10),
        )
        self.svn_cs2 = SubversionChangeSource(
            "/srv/svn/repository",
            cli=MockCli(),
            filters=[(["project", "trunk"], 0, 2)],
            logger=Logger("/data/bb_change_broker.log", 10),
        )
        self.svn_cs3 = SubversionChangeSource(
            "/srv/svn/repository",
            cli=MockCli(),
            filters=[(["project", "-trunk"], 0, 2)],
            logger=Logger("/data/bb_change_broker.log", 10),
        )

    def test_get_changes(self):
        changes = self.svn_cs1.get_changes()
        exp_changes = [
            {
                "branch": "",
                "revision": "1",
                "repository": "/srv/svn/repository",
                "comments": "Update",
                "author": "root",
                "files": ["project/trunk/README.md"],
            },
        ]
        changes = sorted(changes, key=lambda k: k["revision"])
        exp_changes = sorted(exp_changes, key=lambda k: k["revision"])
        for id, change in enumerate(changes):
            for key, value in change.items():
                self.assertEqual(value, exp_changes[id][key])

    def test_get_changes2(self):
        changes = self.svn_cs2.get_changes()
        exp_changes = [
            {
                "branch": "project/trunk",
                "revision": "1",
                "repository": "/srv/svn/repository",
                "comments": "Update",
                "author": "root",
                "files": ["README.md"],
            },
        ]
        changes = sorted(changes, key=lambda k: k["revision"])
        exp_changes = sorted(exp_changes, key=lambda k: k["revision"])
        for id, change in enumerate(changes):
            for key, value in change.items():
                self.assertEqual(value, exp_changes[id][key])

    def test_get_changes3(self):
        changes = self.svn_cs3.get_changes()
        exp_changes = [
            {
                "branch": "",
                "revision": "1",
                "repository": "/srv/svn/repository",
                "comments": "Update",
                "author": "root",
                "files": ["project/trunk/README.md"],
            },
        ]
        changes = sorted(changes, key=lambda k: k["revision"])
        exp_changes = sorted(exp_changes, key=lambda k: k["revision"])
        for id, change in enumerate(changes):
            for key, value in change.items():
                self.assertEqual(value, exp_changes[id][key])

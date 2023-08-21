import unittest, sys, os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mock"))

from mock.cli import MockCli
from bb_change_broker.change_source.git import GitChangeSource
from bb_change_broker.util.log import Logger


class TestGitChangeSource(unittest.TestCase):
    """Test the git change source."""

    def setUp(self):
        """Set up the test."""
        self.git_change_source = GitChangeSource(
            "repository",
            cli=MockCli(),
            logger=Logger(),
        )

    def test_get_changes(self):
        changes = self.git_change_source.get_changes()
        exp_changes = [
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
                "author": "user <User@mail.com>",
                "files": ["somefile.txt"],
                "comments": "New Feature",
            },
            {
                "branch": "master",
                "revision": "24900f9565adfe70eca693610102b5b201720c21",
                "repository": "repository",
                "author": "user <User@mail.com>",
                "files": ["somefile.txt"],
                "comments": "New Feature",
            },
        ]
        changes = sorted(changes, key=lambda k: k["revision"])
        exp_changes = sorted(exp_changes, key=lambda k: k["revision"])
        for id, change in enumerate(changes):
            for key, value in change.items():
                self.assertEqual(value, exp_changes[id][key])

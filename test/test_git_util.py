import unittest, sys, os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mock"))

from mock.cli import MockCli
from bb_change_broker.util.git import (
    is_zero,
    extract_author,
    extract_files,
    extract_comments,
    extract_branch,
    extract_files_from_diff,
    extract_rev,
)


class TestGit(unittest.TestCase):
    def setUp(self) -> None:
        self.cli = MockCli()

    def test_is_zero(self):
        self.assertTrue(is_zero("000"))

    def test_is_zero_with_non_zero(self):
        self.assertFalse(is_zero("001"))

    def test_get_commit_author(self):
        output = self.cli.get_git_commit_info("")
        self.assertEqual(extract_author(output), "user <User@mail.com>")

    def test_get_commit_files(self):
        output = self.cli.get_git_commit_info("")
        self.assertEqual(extract_files(output), ["somefile.txt"])

    def test_get_commit_comments(self):
        output = self.cli.get_git_commit_info("")
        self.assertEqual(extract_comments(output), "New Feature")

    def test_extract_branch(self):
        self.assertEqual(extract_branch("refs/heads/master"), "master")

    def test_extract_files_from_diff(self):
        output = self.cli.get_git_diff("", "")
        self.assertEqual(extract_files_from_diff(output), ["FILE1.txt", "FILE2.txt"])

    def test_extract_rev(self):
        output = self.cli.get_git_commits("", "", "")
        self.assertEqual(
            extract_rev(output.split("\n")[0]),
            "24900f9565adfe70eca693610102b5b201720c21",
        )
        self.assertEqual(
            extract_rev(output.split("\n")[1]),
            "83060a21145596e42d985c798c32aa4b581b7b4f",
        )

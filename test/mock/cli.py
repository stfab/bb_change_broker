from bb_change_broker.backend.cli import BaseCli


class MockCli(BaseCli):
    """Mock implementation of the cli."""

    def __init__(self, *args, **kwargs):
        pass

    def get_svn_commit_author(self, rev_arg, repository):
        return "root"

    def get_svn_commit_revision(self, rev_arg, repository):
        return "1"

    def get_svn_commit_message(self, rev_arg, repository):
        return "Update"

    def get_svn_changed(self, rev_arg, repository):
        return "U   project/trunk/README.md"

    def get_git_stdin(self):
        return [(
            "24900f9565adfe70eca693610102b5b201720c21",
            "83060a21145596e42d985c798c32aa4b581b7b4f",
            "refs/heads/master",
        )]

    def get_git_commits(
        self, refname, newrev, baserev, first_parent=True, new_branch=True
    ):
        return (
            "24900f9565adfe70eca693610102b5b201720c21 bla\n"
            + "83060a21145596e42d985c798c32aa4b581b7b4f Merge branch 'feature/test'"
        )

    def get_git_merge_base(self, oldrev, newrev):
        return "f5934acec8193597e0ee60e1be99b0c18654a222"

    def get_git_commit_info(self, rev):
        return (
            "Author: user <User@mail.com>\n"
            + "Commit: user <User@mail.com>\n"
            + "\n"
            + "    New Feature\n"
            + "\n"
            + ":000000 100644 0000000 7b57bd2 A        somefile.txt"
        )

    def get_git_diff(self, oldrev, newrev):
        return (
            ":100644 000000 ad6d56b 0000000 D        FILE1.txt\n"
            + ":100644 000000 e69de29 0000000 D        FILE2.txt"
        )

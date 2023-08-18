"""Git change source."""

from bb_change_broker.change_source.base import BaseChangeSource
from bb_change_broker.backend.cli import DefaultCli
from bb_change_broker.util.general import add_if_ex
from bb_change_broker.util.git import (
    extract_author,
    extract_files,
    extract_files_from_diff,
    extract_comments,
    extract_rev,
    extract_branch,
    is_zero,
)


class GitChangeSource(BaseChangeSource):
    """Git change source."""

    def __init__(
        self,
        repository,
        logger,
        encoding="utf-8",
        first_parent=True,
        cli=DefaultCli(),
    ):
        """Initialize the git change source.

        :param repository (str): The repository path.
        :param codebase (str): The codebase path.
        :param encoding (str): The encoding of the git log.
        :param logger (bb_change_broker.util.log.Logger): The logger.
        :param first_parent (bool): The first parent flag controls if
            only the first parent of a merge commit is considered.
        :param cli (object): The cli.
        """
        self.repository = repository
        self.encoding = encoding
        self.logger = logger
        self.first_parent = first_parent
        self.cli = cli

    def get_changes(self) -> list:
        """Get the changes.

        :return (list): The changes.
        """
        changes = []

        # XXX: Read from stdin because the git hook writes the data for each ref
        # into stdin. It is not possible to get the info which refs have
        # been updated during the latest push.
        for oldrev, newrev, refname in self.cli.get_git_stdin():
            branch = extract_branch(refname)
            self.logger.debug(
                "oldrev: %s, newrev: %s, refname: %s, branch: %s",
                oldrev,
                newrev,
                refname,
                branch,
            )
            if branch:
                changes.extend(
                    self.__get_commits_by_branch(oldrev, newrev, refname, branch)
                )
        self.logger.info("got git changes: %s", changes)
        return changes

    def __get_commits_by_branch(self, oldrev, newrev, refname, branch) -> list:
        """Get the commits by branch.

        :param oldrev (str): The old revision.
        :param newrev (str): The new revision.
        :param refname (str): The refname.
        :param branch (str): The branch.
        :return (list): The commits.
        """
        return (
            self.__get_commits_on_create(newrev, refname, branch)
            if is_zero(oldrev)  # was branch created?
            else (
                self.__get_commits_on_update(oldrev, newrev, refname, branch)
                if not is_zero(newrev)  # was branch deleted?
                else []
            )
        )

    def __get_commits_on_create(self, newrev, refname, branch) -> list:
        """Get the commits on create.

        :param newrev (str): The new revision.
        :param refname (str): The refname.
        :param branch (str): The branch.
        :return (list): The commits.
        """
        self.logger.debug("get_commits_on_create")
        return self.extract_commits(
            self.cli.get_git_commits(
                refname, newrev, None, self.first_parent, new_branch=True
            ),
            branch,
        )

    def __get_commits_on_update(self, oldrev, newrev, refname, branch) -> list:
        """Get the commits on update.

        :param oldrev (str): The old revision.
        :param newrev (str): The new revision.
        :param refname (str): The refname.
        :param branch (str): The branch.
        :return (list): The commits.
        """
        self.logger.debug("get_commits_on_update")
        changes = []
        baserev = self.cli.get_git_merge_base(oldrev, newrev)
        self.logger.debug("baserev: %s", baserev)
        if baserev != oldrev:  # force push, first rewind to common base
            self.logger.debug("force push")
            changes.extend(self.__get_rewind_commit(oldrev, baserev, branch))
        if newrev != baserev:  # normal update
            self.logger.debug("normal update")
            changes.extend(
                self.__get_commits_between_revs(newrev, refname, branch, baserev)
            )
        return changes

    def __get_rewind_commit(self, oldrev, baserev, branch) -> dict:
        """Create an artificial rewind commit to go back to the common base if
            a force push overwrites the history.

        :param oldrev (str): The old revision.
        :param baserev (str): The base revision.
        :param branch (str): The branch.
        :return (dict): The commit.
        """
        self.logger.debug("get_rewind_commit")
        c = {}
        files = extract_files_from_diff(self.cli.get_git_diff(oldrev, baserev))
        self.__add_commit_meta(baserev, branch, c)
        add_if_ex(c, "comments", "rewind")
        add_if_ex(c, "author", "dummy")
        add_if_ex(c, "files", files)
        return [c]

    def __get_commits_between_revs(self, newrev, refname, branch, baserev) -> list:
        """Get the commits between two revisions.

        :param newrev (str): The new revision.
        :param refname (str): The refname.
        :param branch (str): The branch.
        :param baserev (str): The base revision.
        :return (list): The commits.
        """
        self.logger.debug("get_commits_between_revs")
        input = self.cli.get_git_commits(
            refname, newrev, baserev, self.first_parent, new_branch=False
        )
        return [
            self.__get_commit(branch, line) for line in input.split("\n") if line != ""
        ]

    def __get_commit(self, branch, line) -> dict:
        """Get the commit.

        :param branch (str): The branch.
        :param line (str): The line.
        :return (dict): The commit.
        """
        self.logger.debug("get_commit")
        c = {}
        rev = extract_rev(line)
        self.__add_commit_meta(rev, branch, c)
        commit_info = self.cli.get_git_commit_info(rev)
        c["author"] = extract_author(commit_info)
        c["files"] = extract_files(commit_info)
        c["comments"] = extract_comments(commit_info)
        self.logger.debug("commit: %s", c)
        return c

    def __add_commit_meta(self, baserev, branch, c):
        """Add general commit information.

        :param baserev (str): The base revision.
        :param branch (str): The branch.
        :param c (dict): The commit.
        """
        add_if_ex(c, "branch", str(branch))
        add_if_ex(c, "revision", baserev)
        add_if_ex(c, "repository", self.repository)

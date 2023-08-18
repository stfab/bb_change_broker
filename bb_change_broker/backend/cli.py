"""Abstracts the command line interface."""
import sys

from bb_change_broker.util.cli import check_output


class BaseCli(object):
    """Base class for cli."""

    def __init__(self):
        """Initialize the base cli."""
        pass

    def get_svn_commit_message(self, rev_arg, repository):
        """Get the svn message.

        :param rev_arg (str): The revision arg.
        :param repository (str): The repository path.
        :return (str): The svn commit message.
        """
        pass

    def get_svn_commit_author(self, rev_arg, repository):
        """Get the svn commit author.

        :param rev_arg (str): The revision arg.
        :param repository (str): The repository path.
        :return (str): The svn commit author.
        """
        pass

    def get_svn_commit_revision(self, rev_arg, repository):
        """Get the svn commit revision.

        :param rev_arg (str): The revision arg.
        :param repository (str): The repository path.
        :return (str): The svn commit revision.
        """
        pass

    def get_svn_changed(self, rev_arg, repository):
        """Get the svn changed.

        :param rev_arg (str): The revision arg.
        :param repository (str): The repository path.
        :return (str): The svn changed files list.
        """
        pass

    def get_git_commits(
        self, refname, newrev, baserev, first_parent=True, new_branch=True
    ):
        """Get the git commits.

        :param refname (str): The refname.
        :param newrev (str): The new revision.
        :param baserev (str): The base revision.
        :param first_parent (bool): The first parent flag controls if
            only the first parent of a merge commit is considered.
        :param new_branch (bool): The new branch flag controls if
            only the new branch commits are considered.
        :return (str): The git commits.
        """
        pass

    def get_git_merge_base(self, oldrev, newrev):
        """Get the git merge base.

        :param oldrev (str): The old revision.
        :param newrev (str): The new revision.
        :return (str): The git merge base.
        """
        pass

    def get_git_commit_info(self, rev):
        """Get the git commit info.

        :param rev (str): The revision.
        :return (str): The git commit info.
        """
        pass

    def get_git_diff(self, oldrev, newrev):
        """Get the git diff.

        :param oldrev (str): The old revision.
        :param newrev (str): The new revision.
        :return (str): The git diff.
        """
        pass


class DefaultCli(BaseCli):
    """Default implementation of the cli."""

    def get_svn_commit_message(self, rev_arg, repository, encoding="utf-8"):
        """Get the svn message.

        :param rev_arg (str): The revision arg.
        :param repository (str): The repository path.
        :param encoding (str): The encoding.
        :return (str): The svn commit message.
        """
        return check_output('svnlook log %s "%s"' % (rev_arg, repository)).decode(
            encoding
        )

    def get_svn_commit_author(self, rev_arg, repository, encoding="utf-8"):
        """Get the svn commit author.

        :param rev_arg (str): The revision arg.
        :param repository (str): The repository path.
        :param encoding (str): The encoding.
        :return (str): The svn commit author.
        """
        return check_output('svnlook author %s "%s"' % (rev_arg, repository)).decode(
            encoding
        )

    def get_svn_commit_revision(self, rev_arg, repository, encoding="utf-8"):
        """Get the svn commit revision.

        :param rev_arg (str): The revision arg.
        :param repository (str): The repository path.
        :param encoding (str): The encoding.
        :return (str): The svn commit revision.
        """
        return check_output("svnlook youngest %s" % (repository)).decode(encoding)

    def get_svn_changed(self, rev_arg, repository, encoding="utf-8"):
        """Get the svn changed.

        :param rev_arg (str): The revision arg.
        :param repository (str): The repository path.
        :param encoding (str): The encoding.
        :return (str): The svn changed files list.
        """
        return check_output("svnlook changed %s %s" % (rev_arg, repository)).decode(
            encoding
        )

    def get_git_stdin(self):
        """Get the git stdin.

        :return (list): The git stdin.
        """
        return [line.split() for line in sys.stdin.readlines()]

    def get_git_commits(
        self,
        refname,
        newrev,
        baserev,
        first_parent=True,
        new_branch=True,
        encoding="utf-8",
    ):
        """Get the git commits.

        :param refname (str): The refname.
        :param newrev (str): The new revision.
        :param baserev (str): The base revision.
        :param first_parent (bool): The first parent flag controls if
            only the first parent of a merge commit is considered.
        :param new_branch (bool): The new branch flag controls if
            the branch was newly created. A different logic is used.
        :param encoding (str): The encoding.
        :return (str): The git commits.
        """
        if new_branch:
            return check_output(
                "git rev-parse --not --branches"
                + "| grep -v $(git rev-parse %s)" % refname
                + "| git rev-list --reverse --pretty=oneline --stdin %s" % newrev,
            ).decode(encoding)
        else:
            options = (
                "--reverse --pretty=oneline" + " --first-parent" if first_parent else ""
            )
            return check_output(
                "git rev-list %s %s..%s" % (options, baserev, newrev)
            ).decode(encoding)

    def get_git_merge_base(self, oldrev, newrev, encoding="utf-8"):
        """Get the git merge base.

        :param oldrev (str): The old revision.
        :param newrev (str): The new revision.
        :param encoding (str): The encoding.
        :return (str): The git merge base.
        """
        return (
            check_output("git merge-base %s %s" % (oldrev, newrev))
            .decode(encoding)
            .strip()
        )

    def get_git_commit_info(self, rev, encoding="utf-8"):
        """Get the git commit info.

        :param rev (str): The revision.
        :param encoding (str): The encoding.
        :return (str): The git commit info.
        """
        return check_output("git show --raw --pretty=full %s" % rev).decode(encoding)

    def get_git_diff(self, oldrev, newrev, encoding="utf-8"):
        """Get the git diff.

        :param oldrev (str): The old revision.
        :param newrev (str): The new revision.
        :param encoding (str): The encoding.
        :return (str): The git diff.
        """
        return check_output("git diff --raw %s..%s" % (oldrev, newrev)).decode(
            encoding
        )

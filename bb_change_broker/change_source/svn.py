"""Subversion change source."""

import sys
import re

from bb_change_broker.change_source.base import BaseChangeSource
from bb_change_broker.backend.cli import DefaultCli


class SubversionChangeSource(BaseChangeSource):
    """Subversion change source."""

    def __init__(
        self,
        repository,
        logger,
        filters,
        encoding="utf-8",
        cli=DefaultCli(),
    ):
        """Initialize the subversion change source.

        :param repository (str): The repository of the subversion change source.
        :param logger (Logger): The logger of the subversion change source.
        :param filters (str): The filters for the branch and file name extraction.
        :param encoding (str): The encoding of the subversion change source.
        :param cli (DefaultCli): The cli of the subversion change source.
        """
        self.repository = repository
        self.logger = logger
        self.encoding = encoding
        self.cli = cli
        self.filters = filters

    def get_changes(self):
        """Implementation of get_changes for svn change source."""
        self.logger.info("get_changes for %s" % (self.repository,))
        changed, changestring = self.__get_changestring("")
        self.logger.debug("changed: %s" % (changed,))

        message = self.cli.get_svn_commit_message("", self.repository)
        who = self.cli.get_svn_commit_author("", self.repository)
        revision = self.cli.get_svn_commit_revision("", self.repository)
        self.logger.debug(
            "message: %s, who: %s, revision: %s"
            % (message.strip(), who.strip(), revision.strip())
        )

        return self.__build_changes_msg(
            message, who, revision, self.__get_files_per_branch(changed)
        )

    def __build_changes_msg(self, message, who, revision, files_per_branch):
        """Build the changes message.

        :param message (str): The message of the subversion change source.
        :param who (str): The who of the subversion change source.
        :param revision (str): The revision of the subversion change source.
        :param files_per_branch (dict): The files per branch of the subversion change source.
        :return (list): The changes of the subversion change source.
        """
        return [
            {
                "author": who,
                "repository": self.repository,
                "comments": message,
                "revision": revision,
                "branch": branch if branch else "",
                "files": [
                    file
                    for file in files_per_branch[branch]
                    if file != "" and file != None
                ],
            }
            for branch in files_per_branch.keys()
        ]

    def __get_files_per_branch(self, changed) -> dict:
        """Get the files per branch.

        :param changed (list): The changed of the subversion change source.
        :return (dict): The files per branch of the subversion change source.
        """
        files_per_branch = {}
        for f in changed:
            branch, filename = self.__get_branch_and_file(f)
            if branch in files_per_branch.keys():
                files_per_branch[branch].append(filename)
            else:
                files_per_branch[branch] = [filename]
        return files_per_branch

    def __get_changestring(self, rev_arg) -> tuple:
        """Get the changestring.

        :param rev_arg (str): The revision argument of the subversion change source.
        :return (tuple): The changed and changestring of the subversion change source.
        """
        # XXX: The first 4 columns can contain status information.
        changed = [
            x[4:]
            for x in self.cli.get_svn_changed(rev_arg, self.repository).split("\n")
            if x[4:] != "" and x[4:] != None
        ]
        changestring = "\n".join(changed)
        return changed, changestring

    def __get_branch_and_file(self, path):
        """Split the path into branch and filename.

        :param path (str): The path to split.
        :return (tuple): The branch and filename.
        """
        pieces = path.split("/")
        for filter, f, t in self.filters:
            self.logger.debug("filter: %s" % (filter,))
            self.logger.debug("f: %s" % (f,))
            self.logger.debug("t: %s" % (t,))
            if filter is None or self.__is_branch_dynamic(pieces, filter):
                self.logger.debug("path matches filter %s" % (filter,))
                return self.__extract_dynamic(pieces, f, t)
        self.logger.debug("path does not match any filter")
        return (None, path)

    def __extract_dynamic(self, pieces, f, t):
        """Extract the branch name and files dynamically.

        :param pieces (list): The pieces of the path.
        :param f (int): The start index of the branch name.
        :param t (int): The end index of the branch name.
        :return (tuple): The dynamic branch name.
        """
        return ("/".join(pieces[f:t]), "/".join(pieces[t:]))

    def __is_branch_dynamic(self, pieces, list):
        """Check if the branch is dynamic.

        :param pieces (list): The pieces of the path.
        :param list (list): The list of the branch.
        :return (bool): True if the branch is dynamic, False otherwise.
        """
        for id, el in enumerate(list):
            if el.startswith("-"):
                if pieces[id] == el[1:]:
                    return False
            else:
                if pieces[id] != el:
                    return False
        return True

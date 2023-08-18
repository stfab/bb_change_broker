"""Git utilities."""

import re

AUTHOR_FILTER = r"^Author:\s+(.+)$"
DIFF_FILTER = r"^:.*[MAD]\s+(.+)$"
MERGE_FILTER = r"^Merge: .*$"
COMMIT_FILTER = r"^([0-9a-f]+) (.*)$"
BRANCH_FILTER = r"^refs\/heads\/(.+)$"
ZERO_FILTER = r"^0*$"


def extract_author(commit_info):
    """Extract the author from the commit info.

    :param commit_info: The commit info as a list of lines.
    :return: The author.
    """
    for line in commit_info.split("\n"):
        m = re.match(AUTHOR_FILTER, line)
        if m:
            return str(m.group(1))


def extract_files(commit_info):
    """Extract the files from the commit info.

    :param commit_info: The commit info as a list of lines.
    :return: The files.
    """
    files = []
    for line in commit_info.split("\n"):
        m = re.match(DIFF_FILTER, line)
        if m:
            files.append(str(m.group(1)))
            continue
        if re.match(MERGE_FILTER, line):
            files.append("merge")
    return files


def extract_comments(commit_info):
    """Extract the comments from the commit info.

    :param commit_info: The commit info as a list of lines.
    :return: The comments.
    """
    comments = []
    for line in commit_info.split("\n"):
        if line.startswith(4 * " "):  # XXX: If line starts with four spaces, is comment.
            comments.append(line[4:])
    return "".join(comments)


def extract_branch(refname):
    """Extract the branch from the refname.

    :param refname: The refname.
    :return: The branch.
    """
    m = re.match(BRANCH_FILTER, refname)
    return m.group(1) if m else None


def extract_files_from_diff(input):
    """Extract the files from the diff.

    :param input: The diff.
    :return: The files.
    """
    files = []
    for line in input.split("\n"):
        m = re.match(DIFF_FILTER, line)
        if m:
            files.append(str(m.group(1)))
    return files


def extract_rev(input):
    """Extract the revision from the input.

    :param input: The input.
    :return: The revision.
    """
    m = re.match(COMMIT_FILTER, input.strip())
    return m.group(1) if m else None


def is_zero(rev):
    """Check if the rev is zero.

    :param newrev: The revision.
    :return: True if the branch is deleted, False otherwise.
    """
    return re.match(ZERO_FILTER, rev)

"""Helper functions for the configuration."""


def parse_filters(filters):
    """Parse the filters.

    :param filters (str): The filters of the subversion change source.
    :return (list): The parsed filters.
    """
    ret = []
    for line in filters.split("|"):
        f, t = line.split(",")[-2:]
        ret.append((list(line.split(",")[:-2]), int(f), int(t)))
    return ret

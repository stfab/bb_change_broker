"""General utility functions."""


def add_if_ex(d, key, value):
    """Add a key/value pair to a dictionary if the value exists.

    :param d (dict): The dictionary.
    :param key (str): The key.
    :param value (str): The value.
    """
    if value:
        d[key] = value

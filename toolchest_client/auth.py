"""
toolchest_client.auth
~~~~~~~~~~~~~~~~~~~~~

This module contains functions for configuring the Toolchest authorization key.

"""

import os

def get_key():
    """Retrieves the Toolchest authorization key, if it is configured."""

    try:
        key = os.environ["TOOLCHEST_KEY"]
    except KeyError as e:
        print("Key not found. Please set env var TOOLCHEST_KEY to your specified Toolchest authentication key.")
        print("Function call:")
        print("    toolchest_client.set_key(YOUR_KEY_HERE)")
        return e
    return key

def set_key(key):
    """Sets the Toolchest auth key (TOOLCHEST_KEY) to the given value.

    :param key: key value (str) or path to file containing key. If given a filename,
        the file must consist of only the key itself.

    Usage::

        >>> import toolchest_client as tc
        >>> tc.set_key(YOUR_KEY_HERE)

    """

    if os.path.isfile(key):
        with open(key, "r") as f:
            os.environ["TOOLCHEST_KEY"] = f.read().strip()
    else:
        os.environ["TOOLCHEST_KEY"] = key

# TODO: implement key validation

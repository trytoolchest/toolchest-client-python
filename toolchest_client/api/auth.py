"""
toolchest_client.api.auth
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains functions for configuring the Toolchest API key.

"""

import os
import sys

import requests
from requests.exceptions import HTTPError

from toolchest_client.api.exceptions import ToolchestKeyError


def get_key():
    """Retrieves the Toolchest API key, if it is set."""

    try:
        key = os.environ["TOOLCHEST_KEY"]
    except KeyError as e:
        print("Key not found. Please set environment variable TOOLCHEST_KEY to your Toolchest API key.")
        print("Function call:")
        print("    toolchest_client.set_key(YOUR_KEY_HERE)")
        return e
    return key


def set_key(key):
    """Sets the Toolchest auth key (env var TOOLCHEST_KEY) to the given value.

    :param key: key value (str) or path to file containing key. If given a filename,
        the file must consist of only the key itself.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.set_key(YOUR_KEY_HERE)

    """

    if os.path.isfile(key):
        with open(key, "r") as f:
            os.environ["TOOLCHEST_KEY"] = f.read().strip()
    else:
        os.environ["TOOLCHEST_KEY"] = key


def validate_key():
    """Validates Toolchest API key, retrieved from get_key()."""

    BASE_URL = os.environ.get("BASE_URL", "https://api.toolche.st")
    HEADERS = {"Authorization": f"Key {get_key()}"}

    validation_response = requests.get(
        BASE_URL,
        headers=HEADERS,
    )
    try:
        validation_response.raise_for_status()
    except HTTPError:
        error_message = "Invalid Toolchest auth key. Please check the key value or contact Toolchest."
        print(error_message, file=sys.stderr)
        raise ToolchestKeyError(error_message) from None

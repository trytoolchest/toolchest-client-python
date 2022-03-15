"""
toolchest_client.files.http
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions for handling files given by HTTP / HTTPS URLs.
"""
from json.decoder import JSONDecodeError
from urllib.parse import urlparse

import requests
from requests.exceptions import HTTPError, InvalidURL


def get_url_with_protocol(url):
    """Returns URL with `http://` prepended, if a protocol is not specified.

    :param url: An input URL.
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "http://" + url
    return url


def path_is_http_url(path):
    """Returns whether the given path is an accessible URL by sending a HEAD request.

    :param path: An input path.
    """
    try:
        get_http_url_file_size(get_url_with_protocol(path))
    except (InvalidURL, HTTPError):
        return False

    return True


def get_http_url_file_size(url):
    """Returns file size of an accessible URL, via HEAD metadata.

    :param url: An input URL.
    """
    response = requests.head(url)
    response.raise_for_status()
    try:
        return int(response.json().get('content-length', 0))
    except JSONDecodeError:
        return 0

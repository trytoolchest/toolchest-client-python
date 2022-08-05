"""
toolchest_client.files.public_uris
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions for handling files given by HTTP / HTTPS / FTP URIs.
"""
import os
from ftplib import FTP
from urllib.parse import urlparse
from urllib3.exceptions import LocationParseError

import requests
from requests.exceptions import HTTPError, InvalidURL, InvalidSchema


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
    except (InvalidURL, HTTPError, InvalidSchema, LocationParseError, UnicodeError, Exception):
        return False

    return True


def path_is_accessible_ftp_url(path):
    """Returns whether the given path is an accessible URL by sending a HEAD request.

    :param path: An input path.
    """
    if path.startswith("ftp://"):
        file_size = get_ftp_url_file_size(path)
        return file_size > 0
    return False


def get_http_url_file_size(url):
    """Returns file size of an accessible HTTP URL, via HEAD metadata.

    :param url: An input URL.
    """
    if all([x in url for x in["https://", "s3", "amazonaws.com"]]):
        return 0
    response = requests.head(url)
    response.raise_for_status()
    return int(response.headers.get('content-length', 0))


def get_ftp_url_file_size(url):
    """Returns file size of an accessible FTP URL, via SIZE command.

    :param url: An input URL.
    """
    parsed_url = urlparse(url)
    ftp = FTP(parsed_url.netloc)
    ftp.login()
    return ftp.size(parsed_url.path)

"""
toolchest_client.files.s3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions for handling files in AWS S3 buckets.
"""
import os
import sys

import requests
from requests.exceptions import HTTPError

from toolchest_client.api.auth import get_key
from toolchest_client.api.exceptions import ToolchestS3AccessError


def assert_accessible_s3(uri):
    """Raises an error if the given S3 URI is not accessible by a worker node.

    :param uri: An S3 URI.
    """
    # TODO: move BASE_URL, HEADERS into a new module

    BASE_URL = os.environ.get("BASE_URL", "https://api.toolche.st")
    HEADERS = {"Authorization": f"Key {get_key()}"}

    params = get_params_from_s3_uri(uri)
    response = requests.post(
        f"{BASE_URL}/validate-s3-input/",
        headers=HEADERS,
        json=params,
    )
    try:
        response.raise_for_status()
    except HTTPError:
        error_message = "Given S3 input cannot be accessed by Toolchest."
        print(error_message, file=sys.stderr)
        raise ToolchestS3AccessError(error_message) from None


def get_params_from_s3_uri(uri):
    """Gets the bucket name, key name/path, and ARN of an S3 object from an S3 URI.
    Returns this info in a dict.

    .. note: Assumes S3 bucket is located in a generic AWS region,
      as opposed to China (`aws-cn`) or GovCloud (`aws-us-gov`).

    :param uri: An S3 URI.
    """

    # Index of S3 bucket name in the URI (when split by slashes).
    S3_BUCKET_INDEX = 2
    uri_split = uri.split(sep="/")

    arn = "arn:aws:s3:::" + "/".join(uri_split[S3_BUCKET_INDEX:])
    bucket = uri_split[S3_BUCKET_INDEX]
    key = "/".join(uri_split[S3_BUCKET_INDEX+1:])

    params = {
        "arn": arn,
        "bucket": bucket,
        "key": key,
    }

    return params


def inputs_are_in_s3(input_paths):
    """Returns a list of booleans describing which of the input files are S3 URIs.

    :param input_paths: An input path or list of input paths (strings).
    """
    if isinstance(input_paths, str):
        input_paths = [input_paths]

    S3_PREFIX = "s3://"
    return [file_path.startswith(S3_PREFIX) for file_path in input_paths]

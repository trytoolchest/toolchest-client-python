"""
toolchest_client.files.s3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions for handling files in AWS S3 buckets.
"""
import sys

import requests
from requests.exceptions import HTTPError

from toolchest_client.api.auth import get_headers
from toolchest_client.api.exceptions import ToolchestS3AccessError
from toolchest_client.api.urls import S3_METADATA_URL


def assert_accessible_s3(uri):
    """Raises an error if the given S3 URI is not accessible by a worker node.

    :param uri: An S3 URI.
    """
    try:
        get_s3_file_size(uri)
    except ToolchestS3AccessError as err:
        raise err from None


def get_s3_file_size(uri):
    """Returns the size (in bytes) of a file in S3 that is accessible
    from the worker node.

    :param uri: An S3 URI.
    """
    params = get_params_from_s3_uri(uri)
    response = requests.post(
        S3_METADATA_URL,
        headers=get_headers(),
        json=params,
    )
    try:
        response.raise_for_status()
    except HTTPError:
        error_message = "Given S3 input cannot be accessed by Toolchest."
        print(error_message, file=sys.stderr)
        raise ToolchestS3AccessError(error_message) from None

    return response.json()["file_size"]


def get_params_from_s3_uri(uri):
    """Gets the bucket name, key name/path, and ARN of an S3 object from an S3 URI.
    Returns this info in a dict.

    .. note: Assumes S3 bucket is located in a generic AWS region,
      as opposed to China (`aws-cn`) or GovCloud (`aws-us-gov`).

    :param uri: An S3 URI.
    """

    # Index of S3 bucket name and initial key directory in the URI (when split by slashes).
    S3_BUCKET_INDEX = 2
    S3_KEY_INITIAL_INDEX = S3_BUCKET_INDEX + 1
    uri_split = uri.split(sep="/")

    arn = "arn:aws:s3:::" + "/".join(uri_split[S3_BUCKET_INDEX:])
    bucket = uri_split[S3_BUCKET_INDEX]
    key_initial = uri_split[S3_KEY_INITIAL_INDEX]
    key_final = uri_split[-1]
    key = "/".join(uri_split[S3_KEY_INITIAL_INDEX:])

    params = {
        "arn": arn,
        "bucket": bucket,
        "key": key,
        "key_initial": key_initial,
        "key_final": key_final,
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

"""
toolchest_client.files.s3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions for handling files in AWS S3 buckets.
"""
import os.path
import sys
import threading

import requests
from requests.exceptions import HTTPError

from toolchest_client.api.auth import get_headers
from toolchest_client.api.exceptions import ToolchestS3AccessError
from toolchest_client.api.urls import get_s3_metadata_url


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
        get_s3_metadata_url(),
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


def path_is_s3_uri(path):
    """Returns whether the given path is an S3 URI.

    :param path: An input path.
    """
    # Note: this is just a prefix check and does not validate whether
    #       a file exists at the given URI.
    S3_PREFIX = "s3://"
    return path and path.startswith(S3_PREFIX)


def inputs_are_in_s3(input_paths):
    """Returns a list of booleans describing which of the input files are S3 URIs.

    :param input_paths: An input path or list of input paths (strings).
    """
    if isinstance(input_paths, str):
        input_paths = [input_paths]

    return [path_is_s3_uri(file_path) for file_path in input_paths]


# Slightly modified from https://boto3.amazonaws.com/v1/documentation/api/latest/_modules/boto3/s3/transfer.html
class UploadTracker:
    def __init__(self, file_path):
        self._filename = os.path.basename(file_path)
        if path_is_s3_uri(file_path):
            self._size = get_s3_file_size(file_path)
        else:
            self._size = float(os.path.getsize(file_path))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = round((self._seen_so_far / self._size) * 100, 2)
            print(
                "\r{}  {} / {} bytes ({:.2f}%)".format(
                    self._filename,
                    self._seen_so_far,
                    self._size,
                    percentage
                ).ljust(100),  # pads right end with spaces to flush carriage return
                flush=True
            )
            if percentage == 100.00:  # Adds newline at end of upload
                print()


class DownloadTracker:
    def __init__(self, client, bucket, object_name):
        self._filename = os.path.basename(object_name)
        self._size = client.head_object(Bucket=bucket, Key=object_name)['ContentLength']
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = round((self._seen_so_far / self._size) * 100, 2)
            print(
                "\r{}  {} / {} bytes ({:.2f}%)".format(
                    self._filename,
                    self._seen_so_far,
                    self._size,
                    percentage
                ).ljust(100),  # pads right end with spaces to flush carriage return
                flush=True
            )
            if percentage == 100.00:  # Adds newline at end of download
                print()

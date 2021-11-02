"""
toolchest_client.files.s3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions for handling files in AWS S3 buckets.
"""
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

    arn = convert_s3_uri_to_arn(uri)
    response = requests.get(
        BASE_URL + "/validate-s3-input/",
        headers=HEADERS,
        json={"s3_arn": arn},
    )
    try:
        response.raise_for_status()
    except HTTPError:
        error_message = "Given S3 input cannot be accessed by Toolchest."
        print(error_message, file=sys.stderr)
        raise ToolchestS3AccessError(error_message) from None


def convert_s3_uri_to_arn(uri):
    # TODO: this
    return uri

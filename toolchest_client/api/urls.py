"""
toolchest_client.api.urls
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module serves as a single source for URLs used in
Toolchest queries and API calls.
"""

import os


def get_api_url():
    """Retrieves the base URL for the Toolchest server API. Defaults to "https://api.toolche.st"
    if a custom API URL is not set.
    """
    # Note: BASE_URL is checked for backwards compatibility.
    return os.environ.get("TOOLCHEST_API_URL", os.environ.get("BASE_URL", "https://api.toolche.st"))


def get_pipeline_segment_instances_url():
    """Retrieves the Toolchest API Route for pipeline segment instances. Used internally."""
    PIPELINE_SEGMENT_INSTANCES_ROUTE = "/pipeline-segment-instances"
    return get_api_url() + PIPELINE_SEGMENT_INSTANCES_ROUTE


def get_s3_metadata_url():
    """Retrieves the Toolchest API Route for S3 metadata. Used internally."""
    S3_ROUTE = "/s3"
    S3_URL = get_api_url() + S3_ROUTE
    return S3_URL + "/metadata"


def set_api_url(custom_api_url=None):
    """Sets the Toolchest API URL (env var TOOLCHEST_API_URL) to the given value.
    If a URL is not provided, resets to the default Toolchest API URL.

    :param custom_api_url: Custom API URL. Any trailing slashes should be removed.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.set_api_url("http://your.custom.api.url.here")

    """
    if custom_api_url:
        os.environ["TOOLCHEST_API_URL"] = custom_api_url
    else:
        os.environ.pop("TOOLCHEST_API_URL", None)

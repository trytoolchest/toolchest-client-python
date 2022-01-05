"""
toolchest_client.api.download
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides an interface to download files contained on
the Toolchest server, given access to an API key.

Note: This module is used in downloading from the Output and
Query classes.
"""

import boto3
from botocore.exceptions import ClientError
import requests
from requests.exceptions import HTTPError

from toolchest_client.api.auth import get_headers
from toolchest_client.api.exceptions import ToolchestDownloadError
from toolchest_client.api.urls import PIPELINE_URL
from toolchest_client.files import unpack_files


def download(output_path):
    """Downloads output to ``output_path``."""

    output_file_keys = _get_download_details()

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=output_file_keys["access_key_id"],
            aws_secret_access_key=output_file_keys["secret_access_key"],
            aws_session_token=output_file_keys["session_token"],
        )
        s3_client.download_file(
            output_file_keys["bucket"],
            output_file_keys["object_name"],
            output_path,
        )

    except ClientError as e:
        # TODO: output more detailed error message if write error encountered
        error_message = f"{e} \n\nOutput download failed."
        raise ToolchestDownloadError(error_message) from None


def _get_download_details(pipeline_segment_id):
    """Gets S3 URI and presigned URL for downloading output of query task(s)."""

    response = requests.get(
        "/".join([PIPELINE_URL, pipeline_segment_id, "downloads"]),
        headers=get_headers(),
    )
    try:
        response.raise_for_status()
    except HTTPError:
        error_message = "Download URL retrieval failed."
        raise ToolchestDownloadError(error_message) from None

    response_json = response.json()[0]  # assumes only one output file
    self.output_s3_uri = response_json.get("s3_uri")
    return {
        "access_key_id": response_json.get('access_key_id'),
        "secret_access_key": response_json.get('secret_access_key'),
        "session_token": response_json.get('session_token'),
        "bucket": response_json.get('bucket'),
        "object_name": response_json.get('object_name'),
    }


def _unpack_output(compressed_output_path, output_type):
    """After downloading, unpack files if needed"""
    try:
        unpacked_output_paths = unpack_files(
            file_path_to_unpack=compressed_output_path,
            output_type=output_type,
        )
    except Exception as err:
        error_message = f"Failed to unpack file with type: {output_type}."
        raise ToolchestDownloadError(error_message) from err
    return unpacked_output_paths


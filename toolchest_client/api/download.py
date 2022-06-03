"""
toolchest_client.api.download
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides an interface to download files contained on
the Toolchest server, given access to an API key.

Note: This module is used in downloading from the Output and
Query classes.
"""
import logging
import os
import sys

import boto3
from botocore.exceptions import ClientError
import requests
from requests.exceptions import HTTPError

from toolchest_client.api.auth import get_headers
from toolchest_client.api.exceptions import ToolchestDownloadError
from toolchest_client.api.urls import get_pipeline_segment_instances_url
from toolchest_client.files import get_file_type, get_params_from_s3_uri, unpack_files
from toolchest_client.files.s3 import DownloadTracker


def download(output_path, s3_uri=None, pipeline_segment_instance_id=None, run_id=None,
             output_file_keys=None, skip_decompression=False, output_type=None):
    """Downloads output to `output_path`.

    One of `s3_uri`, `run_id`, or `output_file_keys` must
    be provided. If `output_file_keys` is omitted, this function will attempt to
    extract access keys from `s3_uri` or `run_id` via
    `get_download_details()`.

    :param output_path: Output path to which the file(s) will be downloaded.
        This should be a local directory, but direct filenames are also supported.
    :param s3_uri: URI of file contained in S3. This can be passed from
        the parameter `output.s3_uri` from the `output` returned by a previous
        job.
    :param pipeline_segment_instance_id: (Deprecated) Pipeline segment instance ID of the job
        producing the output you would like to download.
    :param run_id: ID of the job producing the output you would like to download.
    :param output_file_keys: Access keys obtained from `get_download_details()`.
        Used internally.
    :param skip_decompression: Whether to skip decompression of the downloaded file archive.
    :param output_type: Output type of the produced output file. Used internally.
    """

    # pipeline_segment_instance_id as a param is deprecated, remove it as default value eventually
    pipeline_segment_instance_id = run_id or pipeline_segment_instance_id

    if output_file_keys is None:
        if s3_uri:
            # Note: this assumes the pipeline segment instance ID is embedded in the egress S3 URI.
            # This supersedes the pipeline_segment_instance_id, if it is provided.
            s3_uri_params = get_params_from_s3_uri(s3_uri)
            pipeline_segment_instance_id = s3_uri_params["key_initial"]
        if pipeline_segment_instance_id:
            output_s3_uri, output_file_keys = get_download_details(pipeline_segment_instance_id)
        else:
            error_message = "Details of files to download were not provided."
            raise ToolchestDownloadError(error_message) from None

    # If the output path is /path/sample.fastq but the run also has tarred log files, we want to unpack at the directory
    if output_file_keys["primary_name"]:
        output_path = os.path.dirname(output_path)

    # Create output directories if output_path does not exist.
    # Note: Assumes that output_path is a directory if it does not exist.
    # This may lead to undesired leaf dir creation if output_path is not intended to be a dir,
    # but support for non-dir output_path will likely be deprecated.
    output_path = os.path.abspath(os.path.expanduser(output_path))
    if not os.path.exists(output_path) and output_type is None:
        if "." in os.path.basename(output_path):
            logging.warning(f"Creating {os.path.basename(output_path)} as a directory along path {output_path}")
        os.makedirs(output_path, exist_ok=True)

    # If output_path is a directory, extract the filename from the target download.
    if os.path.isdir(output_path):
        file_name = output_file_keys["file_name"]
        output_path = "/".join([output_path, file_name])

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
            Callback=DownloadTracker(s3_client, output_file_keys["bucket"], output_file_keys["object_name"])
        )
    except ClientError as err:
        # TODO: output more detailed error message if write error encountered
        error_message = f"{err} \n\nOutput download failed."
        raise ToolchestDownloadError(error_message) from None

    if skip_decompression:
        return output_path
    unpacked_output_paths = _unpack_output(output_path, output_type=output_type)
    return unpacked_output_paths


def get_download_details(pipeline_segment_instance_id):
    """Gets S3 URI and access keys for downloading output of query task(s)."""

    response = requests.get(
        "/".join([get_pipeline_segment_instances_url(), pipeline_segment_instance_id, "downloads"]),
        headers=get_headers(),
    )
    try:
        response.raise_for_status()
    except HTTPError:
        error_message = ("An error occurred in getting the output S3 URI and download access keys. "
                         f"Pipeline segment instance ID: {pipeline_segment_instance_id}")
        raise ToolchestDownloadError(error_message) from None

    response_json = response.json()[0]  # assumes only one output file
    output_s3_uri = response_json.get("s3_uri")
    output_file_keys = {
        "access_key_id": response_json.get('access_key_id'),
        "secret_access_key": response_json.get('secret_access_key'),
        "session_token": response_json.get('session_token'),
        "bucket": response_json.get('bucket'),
        "object_name": response_json.get('object_name'),
        "file_name": response_json.get('file_name'),
        "primary_name": response_json.get('primary_name'),
    }
    return output_s3_uri, output_file_keys


def _unpack_output(compressed_output_path, output_type=None):
    """After downloading, unpack files if needed"""
    if output_type is None:
        output_type = get_file_type(compressed_output_path)

    try:
        unpacked_output_paths = unpack_files(
            file_path_to_unpack=compressed_output_path,
            output_type=output_type,
        )
    except Exception as err:
        error_message = f"Failed to unpack file with type: {output_type}."
        if sys.platform == "win32":
            PATH_TOO_LONG_CODE = 206
            if isinstance(err, FileNotFoundError) and err.winerror == PATH_TOO_LONG_CODE:
                error_message += "\nLong file name support in Windows 10 must be enabled."
        raise ToolchestDownloadError(error_message) from err
    return unpacked_output_paths

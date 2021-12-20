"""
toolchest_client.api.query
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides a Query object to execute any queries made by Toolchest
tools. These queries are handled by the Toolchest (server) API.
"""

import ntpath
import os
import sys
import threading
import time

import boto3
from botocore.exceptions import ClientError
import requests
from requests.exceptions import HTTPError

from toolchest_client.api.auth import get_key
from toolchest_client.api.exceptions import ToolchestJobError, ToolchestException
from toolchest_client.files import unpack_files, OutputType
from .status import Status, ThreadStatus


class Query():
    """A Toolchest query.

    Provides persistence of query-specific variables from start (query
    creation) to finish (query output download).

    """

    # Base URLs used by the server API.
    BASE_URL = os.environ.get("BASE_URL", "https://api.toolche.st")
    PIPELINE_ROUTE = "/pipeline-segment-instances"
    PIPELINE_URL = BASE_URL + PIPELINE_ROUTE

    # Period (in seconds) between requests when waiting for job(s) to finish executing.
    WAIT_FOR_JOB_DELAY = 1
    # Multiple of seconds used when pretty printing job status to output.
    PRINTED_TIME_INTERVAL = 5

    def __init__(self):
        self.HEADERS = dict()
        self.PIPELINE_SEGMENT_ID = ''
        self.PIPELINE_SEGMENT_URL = ''
        self.STATUS_URL = ''
        self.mark_as_failed = False
        self.thread_name = ''
        self.thread_statuses = None

    def run_query(self, tool_name, tool_version, input_prefix_mapping,
                  output_type, tool_args=None, database_name=None, database_version=None,
                  output_name="output", input_files=None,
                  output_path=None, thread_statuses=None):
        """Executes a query to the Toolchest API.

        :param tool_name: Tool to be used.
        :param tool_version: Version of tool to be used.
        :param tool_args: Tool-specific arguments to be passed to the tool.
        :param database_name: Name of database to be used.
        :param database_version: Version of database to be used.
        :param output_name: (optional) Internal name of file outputted by the tool.
        :param input_files: List of paths to be passed in as input.
        :param output_path: Path (client-side) where the output file will be downloaded.
        :param output_type: Type (e.g. GZ_TAR) of the output file
        :param thread_statuses: Statuses of all threads, shared between threads.
        """
        self.thread_name = threading.current_thread().getName()
        self.thread_statuses = thread_statuses
        self._check_if_should_terminate()

        # Configure Toolchest auth key.
        self.HEADERS["Authorization"] = f"Key {get_key()}"

        # Create pipeline segment and task(s).
        # Retrieve query ID and upload URL from initial response.
        create_response = self._send_initial_request(
            compress_output=True if output_type == OutputType.GZ_TAR else False,
            database_name=database_name,
            database_version=database_version,
            output_name=output_name,
            tool_name=tool_name,
            tool_version=tool_version,
            tool_args=tool_args,
        )
        create_content = create_response.json()

        self._update_thread_status(ThreadStatus.INITIALIZED)

        self.PIPELINE_SEGMENT_ID = create_content["id"]
        self.PIPELINE_SEGMENT_URL = "/".join([
            self.PIPELINE_URL,
            self.PIPELINE_SEGMENT_ID
        ])
        self.STATUS_URL = "/".join([
            self.PIPELINE_SEGMENT_URL,
            "status",
        ])
        self.mark_as_failed = True

        self._check_if_should_terminate()
        self._update_thread_status(ThreadStatus.UPLOADING)
        self._upload(input_files, input_prefix_mapping)
        self._check_if_should_terminate()

        self._update_thread_status(ThreadStatus.EXECUTING)
        self._wait_for_job()

        self._update_thread_status(ThreadStatus.DOWNLOADING)
        self._download(output_path)
        self._unpack_output(output_path, output_type)
        self._update_thread_status(ThreadStatus.COMPLETE)

    def _send_initial_request(self, tool_name, tool_version, tool_args,
                              database_name, database_version, output_name,
                              compress_output):
        """Sends the initial request to the Toolchest API to create the query.

        Returns the response from the POST request.
        """

        create_body = {
            "compress_output": compress_output,
            "custom_tool_args": tool_args,
            "database_name": database_name,
            "database_version": database_version,
            "output_file_name": output_name,
            "tool_name": tool_name,
            "tool_version": tool_version,
        }

        create_response = requests.post(
            self.PIPELINE_URL,
            headers=self.HEADERS,
            json=create_body,
        )
        try:
            create_response.raise_for_status()
        except HTTPError:
            print("Query creation failed.", file=sys.stderr)
            raise

        return create_response

    # Note: input_is_in_s3 is False by default for backwards compatibility.
    # TODO: Deprecate this after confirming it doesn't affect the API.
    def _add_input_file(self, input_file_path, input_prefix, input_is_in_s3=False):
        add_input_file_url = "/".join([
            self.PIPELINE_SEGMENT_URL,
            'input-files'
        ])
        file_name = ntpath.basename(input_file_path)

        response = requests.post(
            add_input_file_url,
            headers=self.HEADERS,
            json={
                "file_name": file_name,
                "tool_prefix": input_prefix,
                "is_s3": input_is_in_s3,
                "s3_uri": input_file_path if input_is_in_s3 else "",
            },
        )
        try:
            response.raise_for_status()
        except HTTPError:
            print(f"Failed to add input file at {input_file_path}", file=sys.stderr)
            raise

        if not input_is_in_s3:
            response_json = response.json()
            return {
                "access_key_id": response_json.get('access_key_id'),
                "secret_access_key": response_json.get('secret_access_key'),
                "session_token": response_json.get('session_token'),
                "bucket": response_json.get('bucket'),
                "object_name": response_json.get('object_name'),
            }

    def _upload(self, input_file_paths, input_prefix_mapping):
        """Uploads the files at ``input_file_paths`` to Toolchest."""

        self._update_status(Status.TRANSFERRING_FROM_CLIENT)

        S3_PREFIX = "s3://"
        for file_path in input_file_paths:
            input_is_in_s3 = file_path.startswith(S3_PREFIX)
            # If the file is already in S3, there is no need to upload.
            if input_is_in_s3:
                # Registers the file in the internal DB.
                self._add_input_file(
                    input_file_path=file_path,
                    input_prefix=input_prefix_mapping.get(file_path),
                    input_is_in_s3=input_is_in_s3,
                )
            else:
                print(f"Uploading {file_path}")
                input_file_keys = self._add_input_file(
                    input_file_path=file_path,
                    input_prefix=input_prefix_mapping.get(file_path),
                    input_is_in_s3=input_is_in_s3,
                )

                try:
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=input_file_keys["access_key_id"],
                        aws_secret_access_key=input_file_keys["secret_access_key"],
                        aws_session_token=input_file_keys["session_token"],
                    )
                    s3_client.upload_file(
                        file_path,
                        input_file_keys["bucket"],
                        input_file_keys["object_name"],
                    )
                except ClientError as e:
                    # todo: this isn't propagating as a failure
                    self._update_status_to_failed(
                        f"{e} \n\nInput file upload failed for file at {file_path}.",
                        force_raise=True
                    )

        self._update_status(Status.TRANSFERRED_FROM_CLIENT)

    def _update_thread_status(self, new_status):
        """
        Updates the shared thread status.
        """
        is_done = new_status == ThreadStatus.FAILED or new_status == ThreadStatus.COMPLETE
        is_interrupting = self.thread_statuses.get(self.thread_name) == ThreadStatus.INTERRUPTING
        if not is_interrupting or is_done:
            self.thread_statuses[self.thread_name] = new_status

    def _update_status(self, new_status):
        """Updates the internal (API) status of the query's task(s).

        Returns the response from the PUT request.
        """

        response = requests.put(
            self.STATUS_URL,
            headers=self.HEADERS,
            json={"status": new_status},
        )
        try:
            response.raise_for_status()
        except HTTPError:
            print("Job status update failed.", file=sys.stderr)
            self._raise_for_failed_response(response)

        return response

    def _update_status_to_failed(self, error_message, force_raise=False, print_msg=True):
        """Updates the internal status of the query's task(s) to 'failed'.

        Includes options to print an error message or raise a ToolchestException.
        To be called when the job fails.
        """
        # Mark thread as failed
        self._update_thread_status(ThreadStatus.FAILED)

        # Mark pipeline segment instance as failed
        requests.put(
            self.STATUS_URL,
            headers=self.HEADERS,
            json={"status": Status.FAILED, "error_message": error_message},
        )
        self.mark_as_failed = False
        if force_raise:
            raise ToolchestException(error_message) from None
        if print_msg:
            print(error_message, file=sys.stderr)

    def _raise_for_failed_response(self, response):
        """Raises an error if a job fails during execution, as indicated by the request response.

        Note: When a job is marked as failed, any requests for current status
        will have a NOT OK status code.
        """
        # Check if there are errors, currently indicated with the "success" descriptor.
        response_body = response.json()
        if "success" in response_body:
            # Failures are currently raised as the catch-all ToolchestException exception.
            if not response_body["success"]:
                # TODO: remove this check once the data error auto-updates status to failed
                if self.mark_as_failed:
                    self._update_status_to_failed(
                        response_body["error"],
                        print_msg=False,
                    )
                raise ToolchestJobError(response_body["error"]) from None

    def _wait_for_job(self):
        """Waits for query task(s) to finish executing."""
        status = self._get_job_status()
        start_time = time.time()
        while status != Status.READY_TO_TRANSFER_TO_CLIENT:
            self._check_if_should_terminate()
            status = self._get_job_status()

            elapsed_time = time.time() - start_time
            leftover_delay = elapsed_time % self.WAIT_FOR_JOB_DELAY
            time.sleep(leftover_delay)

    def _get_job_status(self):
        """Gets status of current job (tasks)."""

        response = requests.get(
            self.STATUS_URL,
            headers=self.HEADERS
        )
        try:
            response.raise_for_status()
        except HTTPError:
            print("Job status retrieval failed.", file=sys.stderr)
            # Assumes a job has already been marked as failed if failure is detected after execution begins.
            self.mark_as_failed = False
            self._raise_for_failed_response(response)

        return response.json()["status"]

    def _download(self, output_path):
        """Downloads output to ``output_path``."""

        output_file_keys = self._get_download()

        self._update_status(Status.TRANSFERRING_TO_CLIENT)

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
            self._update_status_to_failed(
                f"{e} \n\nOutput download failed.",
                force_raise=True
            )

        self._update_status(Status.TRANSFERRED_TO_CLIENT)
        self.mark_as_failed = False

    def _get_download(self):
        """Gets URL for downloading output of query task(s)."""

        response = requests.get(
            "/".join([self.PIPELINE_URL, self.PIPELINE_SEGMENT_ID, "downloads"]),
            headers=self.HEADERS,
        )
        try:
            response.raise_for_status()
        except HTTPError:
            self._update_status_to_failed(
                "Download URL retrieval failed.",
                force_raise=True,
            )

        response_json = response.json()[0]  # assumes only one output file
        return {
            "access_key_id": response_json.get('access_key_id'),
            "secret_access_key": response_json.get('secret_access_key'),
            "session_token": response_json.get('session_token'),
            "bucket": response_json.get('bucket'),
            "object_name": response_json.get('object_name'),
        }

    def _unpack_output(self, output_path, output_type):
        """After downloading, unpack files if needed"""
        try:
            unpack_files(
                file_path_to_unpack=output_path,
                output_type=output_type,
            )
        except Exception as err:
            print(err)
            self._update_status_to_failed(
                f"Failed to unpack file with type: {output_type}.",
                force_raise=True,
            )
            raise err

    def _mark_as_failed_at_exit(self):
        """Upon exit, marks job as failed if it has started but is not marked as completed/failed."""

        # TODO: look at putting this function inside the __init__?
        # otherwise, each Query instance persists until exit

        if self.mark_as_failed:
            self._update_status_to_failed(
                "Client exited before job completion.",
            )

    def _check_if_should_terminate(self):
        """Checks for flag set by parent process to see if it should terminate self."""
        thread_status = self.thread_statuses.get(self.thread_name)
        if thread_status == ThreadStatus.INTERRUPTING:
            self._update_status_to_failed(
                error_message="Terminating due to failure in sibling thread or parent process",
                force_raise=False,
                print_msg=False
            )

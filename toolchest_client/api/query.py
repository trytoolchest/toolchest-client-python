"""
toolchest_client.api.query
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides a Query object to execute any queries made by Toolchest
tools. These queries are handled by the Toolchest (server) API.
"""

import ntpath
import sys
import threading
import time

import boto3
from botocore.exceptions import ClientError
import requests
from requests.exceptions import HTTPError

from toolchest_client.api.auth import get_headers
from toolchest_client.api.download import download, get_download_details
from toolchest_client.api.exceptions import ToolchestJobError, ToolchestException, ToolchestDownloadError
from toolchest_client.api.output import Output
from toolchest_client.api.urls import PIPELINE_SEGMENT_INSTANCES_URL
from toolchest_client.files import OutputType, path_is_s3_uri
from .status import Status, ThreadStatus


class Query:
    """A Toolchest query.

    Provides persistence of query-specific variables from start (query
    creation) to finish (query output download).

    """

    # Period (in seconds) between requests when waiting for job(s) to finish executing.
    WAIT_FOR_JOB_DELAY = 1
    # Multiple of seconds used when pretty printing job status to output.
    PRINTED_TIME_INTERVAL = 5

    def __init__(self, stored_output=None):
        self.HEADERS = dict()
        self.PIPELINE_SEGMENT_INSTANCE_ID = ''
        self.PIPELINE_SEGMENT_INSTANCE_URL = ''
        self.STATUS_URL = ''
        self.mark_as_failed = False
        self.thread_name = ''
        self.thread_statuses = None

        self.unpacked_output_paths = None
        self.output = stored_output if stored_output else Output()

    def run_query(self, tool_name, tool_version, input_prefix_mapping,
                  output_type, tool_args=None, database_name=None, database_version=None,
                  custom_database_path=None, output_name="output", input_files=None,
                  output_path=None, thread_statuses=None):
        """Executes a query to the Toolchest API.

        :param tool_name: Tool to be used.
        :param tool_version: Version of tool to be used.
        :param tool_args: Tool-specific arguments to be passed to the tool.
        :param database_name: Name of database to be used.
        :param database_version: Version of database to be used.
        :param custom_database_path: Path (S3 URI) to a custom database.
        :param input_prefix_mapping: Mapping of input filepaths to associated prefix tags (e.g., "-1")
        :param output_name: (optional) Internal name of file outputted by the tool.
        :param input_files: List of paths to be passed in as input.
        :param output_path: Path (client-side) where the output file will be downloaded.
        :param output_type: Type (e.g. GZ_TAR) of the output file
        :param thread_statuses: Statuses of all threads, shared between threads.
        """
        self.thread_name = threading.current_thread().getName()
        self.thread_statuses = thread_statuses
        self._check_if_should_terminate()

        # Configure Toolchest API authorization.
        self.HEADERS = get_headers()

        # Create pipeline segment and task(s).
        # Retrieve query ID and upload URL from initial response.
        create_response = self._send_initial_request(
            compress_output=True if output_type == OutputType.GZ_TAR else False,
            database_name=database_name,
            database_version=database_version,
            custom_database_path=custom_database_path,
            output_name=output_name,
            tool_name=tool_name,
            tool_version=tool_version,
            tool_args=tool_args,
            output_file_path=output_path,
        )
        create_content = create_response.json()

        self._update_thread_status(ThreadStatus.INITIALIZED)

        self.PIPELINE_SEGMENT_INSTANCE_ID = create_content["id"]
        self.PIPELINE_SEGMENT_INSTANCE_URL = "/".join([
            PIPELINE_SEGMENT_INSTANCES_URL,
            self.PIPELINE_SEGMENT_INSTANCE_ID
        ])
        self.STATUS_URL = "/".join([
            self.PIPELINE_SEGMENT_INSTANCE_URL,
            "status",
        ])
        self.mark_as_failed = True

        self._check_if_should_terminate()
        self._update_thread_status(ThreadStatus.UPLOADING)
        self._upload(input_files, input_prefix_mapping)
        self._check_if_should_terminate()

        self._update_thread_status(ThreadStatus.EXECUTING)
        self._wait_for_job()

        self._download(output_path, output_type)

        self.mark_as_failed = False
        self._update_status(Status.COMPLETE)
        self._update_thread_status(ThreadStatus.COMPLETE)

        self.output.s3_uri = self.output_s3_uri
        self.output.output_path = self.unpacked_output_paths
        return self.output

    def _send_initial_request(self, tool_name, tool_version, tool_args,
                              database_name, database_version, custom_database_path,
                              output_name, compress_output, output_file_path):
        """Sends the initial request to the Toolchest API to create the query.

        Returns the response from the POST request.
        """

        create_body = {
            "compress_output": compress_output,
            "custom_tool_args": tool_args,
            "custom_database_s3_location": custom_database_path,
            "database_name": database_name,
            "database_version": database_version,
            "output_file_name": output_name,
            "tool_name": tool_name,
            "tool_version": tool_version,
            "output_file_path": output_file_path,
        }

        create_response = requests.post(
            PIPELINE_SEGMENT_INSTANCES_URL,
            headers=self.HEADERS,
            json=create_body,
        )
        try:
            create_response.raise_for_status()
        except HTTPError:
            print("Query creation failed.", file=sys.stderr)
            raise

        return create_response

    def _update_file_size(self, fileId):
        update_file_size_url = "/".join([
            PIPELINE_SEGMENT_INSTANCES_URL,
            'input-files',
            fileId,
            'update-file-size'
        ])

        response = requests.put(
            update_file_size_url,
            headers=self.HEADERS,
        )
        try:
            response.raise_for_status()
        except HTTPError:
            print(f"Failed to update size for file: {fileId}", file=sys.stderr)
            raise

    def _register_input_file(self, input_file_path, input_prefix, input_order):
        register_input_file_url = "/".join([
            self.PIPELINE_SEGMENT_INSTANCE_URL,
            'input-files'
        ])
        file_name = ntpath.basename(input_file_path)
        input_is_in_s3 = path_is_s3_uri(input_file_path)

        response = requests.post(
            register_input_file_url,
            headers=self.HEADERS,
            json={
                "file_name": file_name,
                "tool_prefix": input_prefix,
                "tool_prefix_order": input_order,
                "s3_uri": input_file_path if input_is_in_s3 else None,
            },
        )
        try:
            response.raise_for_status()
        except HTTPError:
            print(f"Failed to register input file at {input_file_path}", file=sys.stderr)
            raise

        if not input_is_in_s3:
            response_json = response.json()
            return {
                "access_key_id": response_json.get('access_key_id'),
                "secret_access_key": response_json.get('secret_access_key'),
                "session_token": response_json.get('session_token'),
                "bucket": response_json.get('bucket'),
                "object_name": response_json.get('object_name'),
                "file_id": response_json.get('file_id'),
            }

    def _upload(self, input_file_paths, input_prefix_mapping):
        """Uploads the files at ``input_file_paths`` to Toolchest."""

        self._update_status(Status.TRANSFERRING_FROM_CLIENT)

        for file_path in input_file_paths:
            input_is_in_s3 = path_is_s3_uri(file_path)
            input_prefix_details = input_prefix_mapping.get(file_path)
            input_prefix = input_prefix_details.get("prefix") if input_prefix_details else None
            input_order = input_prefix_details.get("order") if input_prefix_details else None
            # If the file is already in S3, there is no need to upload.
            if input_is_in_s3:
                # Registers the file in the internal DB.
                self._register_input_file(
                    input_file_path=file_path,
                    input_prefix=input_prefix,
                    input_order=input_order,
                )
            else:
                print(f"Uploading {file_path}")
                input_file_keys = self._register_input_file(
                    input_file_path=file_path,
                    input_prefix=input_prefix,
                    input_order=input_order,
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
                    self._update_file_size(input_file_keys["file_id"])
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

    def _download(self, output_path, output_type):
        """Retrieves information needed for downloading. If ``output_path`` is given,
        downloads output to ``output_path`` and decompresses output archive, if necessary.
        """

        try:
            self.output_s3_uri, output_file_keys = get_download_details(self.PIPELINE_SEGMENT_INSTANCE_ID)
            if output_path and not path_is_s3_uri(output_path):
                self._update_thread_status(ThreadStatus.DOWNLOADING)
                self._update_status(Status.TRANSFERRING_TO_CLIENT)
                self.unpacked_output_paths = download(
                    output_path=output_path,
                    output_file_keys=output_file_keys,
                    output_type=output_type,
                )
                self._update_status(Status.TRANSFERRED_TO_CLIENT)
        except ToolchestDownloadError as err:
            self._update_status_to_failed(err)

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

"""
toolchest_client.query
~~~~~~~~~~~~~~~~~~~~~~

This module provides a Query object to execute any queries made by Toolchest
tools. These queries are handled by the Toolchest (server) API.
"""

import atexit
import ntpath
import os
import sys
import threading
import time

import requests
from requests.exceptions import HTTPError

from .auth import get_key
from .exceptions import ToolchestJobError, ToolchestException
from .status import Status


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
        atexit.register(self._mark_as_failed_at_exit)

    def run_query(self, tool_name, tool_version, input_prefix_mapping,
                  tool_args=None, database_name=None, database_version=None,
                  output_name="output", input_files=None, output_path=None,
                  thread_statuses=None):
        """Executes a query to the Toolchest API.

        :param tool_name: Tool to be used.
        :param tool_version: Version of tool to be used.
        :param tool_args: Tool-specific arguments to be passed to the tool.
        :param database_name: Name of database to be used.
        :param database_version: Version of database to be used.
        :param output_name: (optional) Internal name of file outputted by the tool.
        :param input_files: List of paths to be passed in as input.
        :param output_path: Path (client-side) where the output file will be downloaded.
        :param thread_statuses: Statuses of all threads, shared between threads.
        """
        thread_name = threading.current_thread().getName()
        if thread_statuses is None:
            thread_statuses = dict()
        thread_statuses[thread_name] = "Initialized"

        # Retrieve and validate Toolchest auth key.
        self.HEADERS["Authorization"] = f"Key {get_key()}"
        validation_response = requests.get(
            self.BASE_URL,
            headers=self.HEADERS,
        )
        try:
            validation_response.raise_for_status()
        except HTTPError:
            print("Invalid Toolchest auth key. Please check the key value or contact Toolchest.", file=sys.stderr)
            raise

        # Create pipeline segment and task(s).
        # Retrieve query ID and upload URL from initial response.
        create_response = self._send_initial_request(
            tool_name,
            tool_version,
            tool_args,
            database_name,
            database_version,
            output_name,
        )
        create_content = create_response.json()
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

        thread_statuses[thread_name] = "uploading"
        self._upload(input_files, input_prefix_mapping)

        thread_statuses[thread_name] = "executing"
        self._wait_for_job()

        thread_statuses[thread_name] = "downloading"
        self._download(output_path)
        thread_statuses[thread_name] = "complete"

    def _send_initial_request(self, tool_name, tool_version, tool_args,
                              database_name, database_version, output_name):
        """Sends the initial request to the Toolchest API to create the query.

        Returns the response from the POST request.
        """

        create_body = {
            "tool_name": tool_name,
            "tool_version": tool_version,
            "custom_tool_args": tool_args,
            "database_name": database_name,
            "database_version": database_version,
            "output_file_name": output_name,
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

    def _add_input_file(self, input_file_path, input_prefix):
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
            },
        )
        try:
            response.raise_for_status()
        except HTTPError:
            print(f"Failed to upload file at {input_file_path}", file=sys.stderr)
            raise
        return response.json().get("input_file_upload_location")

    def _upload(self, input_file_paths, input_prefix_mapping):
        """Uploads the files at ``input_file_paths`` to Toolchest."""

        self._update_status(Status.TRANSFERRING_FROM_CLIENT)

        for file_path in input_file_paths:
            print(f"Uploading {file_path}")
            upload_url = self._add_input_file(
                input_file_path=file_path,
                input_prefix=input_prefix_mapping.get(file_path)
            )

            upload_response = requests.put(
                upload_url,
                data=open(file_path, "rb")
            )
            try:
                upload_response.raise_for_status()
            except HTTPError as e:
                # todo: this isn't propagating as a failure
                self._update_status_to_failed(
                    f"Input file upload failed for file at {file_path}.",
                    force_raise=True
                )

        self._update_status(Status.TRANSFERRED_FROM_CLIENT)

    def _update_status(self, new_status):
        """Updates the internal status of the query's task(s).

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
                    self.mark_as_failed = False
                raise ToolchestJobError(response_body["error"]) from None

    def _wait_for_job(self):
        """Waits for query task(s) to finish executing."""
        status = self._get_job_status()
        start_time = time.time()
        while status != Status.READY_TO_TRANSFER_TO_CLIENT:
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

        download_signed_url = self._get_download_signed_url()

        self._update_status(Status.TRANSFERRING_TO_CLIENT)

        # Downloads output by sending a GET request.
        with requests.get(download_signed_url, stream=True) as r:
            # Validates response of GET request.
            try:
                r.raise_for_status()
            except HTTPError:
                self._update_status_to_failed(
                    "Output download failed.",
                    force_raise=True,
                )

            # Writes streamed output data from response to the output file.
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            # TODO: output more detailed error message if write error encountered

        self._update_status(Status.TRANSFERRED_TO_CLIENT)

    def _get_download_signed_url(self):
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

        # TODO: add support for multiple download files

        return response.json()[0]["signed_url"]

    def _mark_as_failed_at_exit(self):
        """Upon exit, marks job as failed if it has started but is not marked as completed/failed."""

        # TODO: look at putting this function inside the __init__?
        # otherwise, each Query instance persists until exit

        if self.mark_as_failed:
            status = self._get_job_status()
            self._update_status_to_failed(
                "Client exited before job completion.",
            )
            self.mark_as_failed = False

"""
toolchest_client.query
~~~~~~~~~~~~~~~~~~~~~~

This module provides a Query object to execute any queries made by Toolchest
tools. These queries are handled by the Toolchest (server) API.
"""

import os
import ntpath
import time

import requests
from requests.exceptions import HTTPError

from .auth import get_key
from .exceptions import DataLimitError
from .files import files_in_path
from .status import Status


def _validate_args(output_name, input_path, output_path):
    """Checks if query args are correctly formatted."""

    if input_path is None:
        raise FileNotFoundError("input file path must be specified")  # temp error message
        # TODO: implement file selection

    if output_path is None:
        raise FileNotFoundError("output file path must be specified")  # temp error message
        # TODO: implement file selection
    try:
        with open(output_path, "a") as f:
            pass
    except OSError:
        raise OSError("output file path must be writable")

    if not output_name:
        raise ValueError("output name must be non-empty")
    # TODO: complete implementing argument checking


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
    # Buffer on print statements for job status updates, to make carriage returns pretty.
    JOB_STATUS_BUFFER = " " * 50

    def __init__(self):
        self.HEADERS = dict()
        self.PIPELINE_SEGMENT_ID = ''
        self.PIPELINE_SEGMENT_URL = ''
        self.STATUS_URL = ''

    def run_query(self, tool_name, tool_version, tool_args=None,
                  database_name=None, database_version=None,
                  output_name="output", input_path=None, output_path=None):
        """Executes a query to the Toolchest API.

        :param tool_name: Tool to be used.
        :param tool_version: Version of tool to be used.
        :param tool_args: Tool-specific arguments to be passed to the tool.
        :param database_name: Name of database to be used.
        :param database_version: Version of database to be used.
        :param output_name: (optional) Internal name of file outputted by the tool.
        :param input_path: Path (client-side) to a file or directory to be passed in as input.
        :param output_path: Path (client-side) where the output file will be downloaded.
        """

        _validate_args(
            output_name,
            input_path,
            output_path,
        )

        # Retrieve and validate Toolchest auth key.
        self.HEADERS["Authorization"] = f"Key {get_key()}"
        validation_response = requests.get(
            self.BASE_URL,
            headers=self.HEADERS,
        )
        try:
            validation_response.raise_for_status()
        except HTTPError:
            print("Invalid Toolchest auth key. Please check the key value or contact Toolchest.")
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

        print("Uploading...")
        files_to_upload = files_in_path(input_path)
        print(f"Found {len(files_to_upload)} files to upload.")
        self._upload(files_to_upload)
        print("Uploaded!")

        print("Executing job...")
        self._wait_for_job()
        print("Job complete!" + self.JOB_STATUS_BUFFER)

        print("Downloading...")
        self._download(output_path)
        print("Downloaded!")

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
            print("Query creation failed.")
            raise

        return create_response

    def _add_input_file(self, input_file_path):
        add_input_file_url = "/".join([
            self.PIPELINE_SEGMENT_URL,
            'input-files'
        ])
        file_name = ntpath.basename(input_file_path)

        response = requests.post(
            add_input_file_url,
            headers=self.HEADERS,
            json={"file_name": file_name},
        )
        try:
            response.raise_for_status()
        except HTTPError:
            print(f"Failed to upload file at {input_file_path}")
            raise
        return response.json().get("input_file_upload_location")

    def _upload(self, input_file_paths):
        """Uploads the files at ``input_file_paths`` to Toolchest."""

        self._update_status(Status.TRANSFERRING_FROM_CLIENT.value)

        for file_path in input_file_paths:
            print(f"Uploading {file_path}")
            upload_url = self._add_input_file(file_path)

            upload_response = requests.put(
                upload_url,
                data=open(file_path, "rb")
            )
            try:
                upload_response.raise_for_status()
            except HTTPError:
                print(f"Input file upload failed for file at {file_path}")
                raise

        self._update_status(Status.TRANSFERRED_FROM_CLIENT.value)

    def _update_status(self, new_status):
        """Updates the internal status of the query's task(s).

        Returns the response from the PUT request.
        """
        print('status url', self.STATUS_URL)
        response = requests.put(
            self.STATUS_URL,
            headers=self.HEADERS,
            json={"status": new_status},
        )
        try:
            response.raise_for_status()
        except HTTPError:
            print("Job status update failed." + self.JOB_STATUS_BUFFER)

            # Check if there are errors.
            response_body = response.json()
            if "success" in response_body:
                # Failures are currently assumed to be solely due to data limits.
                if not response_body["success"]:
                    raise DataLimitError(response_body["error"]) from None
            raise

        return response

    def _pretty_print_job_status(self, job_status, elapsed_time):
        pretty_status = ''
        for index, word in enumerate(job_status.split('_')):
            pretty_status += word.title() if index == 0 else f" {word}"
        status_line = "".join([
            "Job status: ",
            pretty_status,
            " (",
            str(int(elapsed_time) // self.PRINTED_TIME_INTERVAL * self.PRINTED_TIME_INTERVAL),
            "s)",
            self.JOB_STATUS_BUFFER,
        ])
        print(status_line, end="\r")

    def _wait_for_job(self):
        """Waits for query task(s) to finish executing."""
        status = self._get_job_status()
        start_time = time.time()
        while status != Status.READY_TO_TRANSFER_TO_CLIENT.value:
            status = self._get_job_status()

            elapsed_time = time.time() - start_time
            self._pretty_print_job_status(status, elapsed_time)

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
            print("Job status retrieval failed.")
            raise

        return response.json()["status"]

    def _download(self, output_path):
        """Downloads output to ``output_path``."""

        download_signed_url = self._get_download_signed_url()

        self._update_status(Status.TRANSFERRING_TO_CLIENT.value)

        # Dowloads output by sending a GET request.
        with requests.get(download_signed_url, stream=True) as r:
            # Validates reponse of GET request.
            try:
                r.raise_for_status()
            except HTTPError:
                print("Output download failed.")
                raise

            # Writes streamed output data from response to the output file.
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        self._update_status(Status.TRANSFERRED_TO_CLIENT.value)

    def _get_download_signed_url(self):
        """Gets URL for downloading output of query task(s)."""

        response = requests.get(
            "/".join([self.PIPELINE_URL, self.PIPELINE_SEGMENT_ID, "downloads"]),
            headers=self.HEADERS,
        )
        try:
            response.raise_for_status()
        except HTTPError:
            print("Download URL retrieval failed.")
            raise

        # TODO: add support for multiple download files

        return response.json()[0]["signed_url"]

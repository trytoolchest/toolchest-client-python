"""
toolchest_client.query
~~~~~~~~~~~~~~~~~~~~~~

This module provides a Query object to execute any queries made by Toolchest
tools. These queries are handled by the Toolchest (server) API.
"""

import os
import time

import requests
from requests.exceptions import HTTPError

from .auth import get_key
from .exceptions import DataLimitError
from .status import Status

class Query():
    """A Toolchest query.

    Provides persistence of query-specific variables from start (query
    creation) to finish (query output download).

    """

    # Base URLs used by the server API.
    BASE_URL = "http://toolchest.us-east-1.elasticbeanstalk.com"
    PIPELINE_ROUTE = "/pipeline-segment-instances"
    PIPELINE_URL = BASE_URL + PIPELINE_ROUTE

    # Period (in seconds) between requests when waiting for job(s) to finish executing.
    WAIT_FOR_JOB_DELAY = 1
    # Multiple of seconds used when pretty printing job status to output.
    PRINTED_TIME_INTERVAL = 5
    # Buffer on print statements for job status updates, to make carriage returns pretty.
    JOB_STATUS_BUFFER = " "*50

    def run_query(self, tool_name, tool_version,
            tool_args=None, input_name="input", output_name="output",
            input_path=None, output_path=None):
        """Executes a query to the Toolchest API.

        :param tool_name: Tool to be used.
        :param tool_version: Version of tool to be used.
        :param tool_args: Tool-specific arguments to be passed to the tool.
        :param input_name: (optional) Internal name of file inputted to the tool.
        :param output_name: (optional) Internal name of file outputted by the tool.
        :param input_path: Path (client-side) of file to be passed in as input.
        :param output_path: Path (client-side) where the output file will be downloaded.
        """

        self._validate_args(
            input_name,
            output_name,
            input_path,
            output_path,
        )

        # Retrieve and validate Toolchest auth key.
        key = get_key()
        self.HEADERS = {"Authorization": "Key " + key}
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
            input_name,
            output_name,
        )
        create_content = create_response.json()
        self.PIPELINE_SEG_ID = create_content["id"]
        self.STATUS_URL = "/".join([
            self.PIPELINE_URL,
            self.PIPELINE_SEG_ID,
            "status",
        ])
        self.UPLOAD_URL = create_content["input_file_upload_location"]

        print("Uploading...")
        self._upload(input_path)
        print("Uploaded!")

        print("Executing job...")
        self._wait_for_job()
        print("Job complete!" + self.JOB_STATUS_BUFFER)

        print("Downloading...")
        self._download(output_path)
        print("Downloaded!")

    def _validate_args(self, input_name, output_name, input_path, output_path):
        """Checks if query args are correctly formatted."""

        if input_path is None:
            raise FileNotFoundError("input file path must be specified") # temp error message
            # TODO: implement file selection
        elif not os.path.isfile(input_path):
            raise FileNotFoundError("input file path must be a valid file")

        if output_path is None:
            raise FileNotFoundError("output file path must be specified") # temp error message
            # TODO: implement file selection
        try:
            with open(output_path, "a") as f:
                pass
        except OSError:
            raise OSError("output file path must be writable")

        if not input_name:
            raise ValueError("input name must be non-empty")
        if not output_name:
            raise ValueError("output name must be non-empty")
        # TODO: complete implementing argument checking

    def _send_initial_request(self, tool_name, tool_version,
            tool_args, input_name, output_name):
        """Sends the initial request to the Toolchest API to create the query.

        Returns the response from the POST request.
        """

        create_body = {
            "tool_name": tool_name,
            "tool_version": tool_version,
            "database_name": None,
            "database_version": None,
            "input_file_name": input_name,
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

    def _upload(self, input_path):
        """Uploads the file at ``input_path`` to Toolchest."""

        self._update_status(Status.TRANSFERRING_FROM_CLIENT.value)

        upload_response = requests.put(
            self.UPLOAD_URL,
            data=open(input_path, "rb")
        )
        try:
            upload_response.raise_for_status()
        except HTTPError:
            print("Input file upload failed.")
            raise

        self._update_status(Status.TRANSFERRED_FROM_CLIENT.value)

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
            "/".join([self.PIPELINE_URL, self.PIPELINE_SEG_ID, "downloads"]),
            headers=self.HEADERS,
        )
        try:
            response.raise_for_status()
        except HTTPError:
            print("Download URL retrieval failed.")
            raise

        # TODO: add support for multiple download files

        return response.json()[0]["signed_url"]

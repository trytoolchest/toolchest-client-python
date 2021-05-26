import os
import time

import requests

from .auth import get_key
from .status import Status

class Query():
    BASE_URL = "http://toolchest.us-east-1.elasticbeanstalk.com"
    PIPELINE_ROUTE = "/pipeline-segment-instances"
    PIPELINE_URL = BASE_URL + PIPELINE_ROUTE

    WAIT_FOR_JOB_DELAY = 15

    def run_query(self, tool_name, tool_version,
            tool_args=None, input_name="input", output_name="output",
            input_path=None, output_path=None):
        self._validate_args(
            input_path,
            output_path,
            input_name,
            output_name,
        )

        key = get_key()
        self.HEADERS = {"Authorization": "Key " + key}

        create_response = self._send_initial_request(
            tool_name,
            tool_version,
            tool_args,
            input_name,
            output_name,
        )
        create_content = create_response.json()
        self.CUSTOMER_ID = create_content["id"]
        self.STATUS_URL = "/".join([
            self.PIPELINE_URL,
            self.CUSTOMER_ID,
            "status",
        ])
        self.UPLOAD_URL = create_content["input_file_upload_location"]

        print("Uploading...")
        self._upload(input_path)
        print("Uploaded!")

        print("Executing job...")
        self._wait_for_job()
        print("Job complete!")

        print("Downloading...")
        self._download(output_path)
        print("Downloaded!")

    def _validate_args(self, input_path, output_path, input_name, output_name):
        if input_path is None:
            raise FileNotFoundError("input file path must be specified") # temp error message
            # TODO: implement file selection
        elif not os.path.isfile(input_path):
            raise FileNotFoundError("input file path must be a valid file")

        if output_path is None:
            raise FileNotFoundError("output file path must be specified") # temp error message
            # TODO: implement file selection
        elif not os.access(output_path, os.W_OK):
            raise ValueError("output file path must be writable")

        if not input_name:
            raise ValueError("input name must be non-empty")
        if not output_name:
            raise ValueError("output name must be non-empty")
        # TODO: complete implementing argument checking

    def _send_initial_request(self, tool_name, tool_version,
            tool_args, input_name, output_name):
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
        create_response.raise_for_status()

        return create_response

    def _upload(self, input_path):
        # TODO: check if input path is NULL, add user file selection

        self._update_status(Status.TRANSFERRING_FROM_CLIENT.value)

        upload_response = requests.put(
            self.UPLOAD_URL,
            data=open(input_path, "rb")
        )
        upload_response.raise_for_status()

        self._update_status(Status.TRANSFERRED_FROM_CLIENT.value)

    def _update_status(self, new_status):
        response = requests.put(
            self.STATUS_URL,
            headers=self.HEADERS,
            json={"status": new_status},
        )
        response.raise_for_status()
        return response

    def _wait_for_job(self):
        status = self._get_job_status()
        print(status)
        while status != Status.READY_TO_TRANSFER_TO_CLIENT.value:
            time.sleep(self.WAIT_FOR_JOB_DELAY)
            status = self._get_job_status()
            print(status)

    def _get_job_status(self):
        response = requests.get(
            self.STATUS_URL,
            headers=self.HEADERS
        )
        response.raise_for_status()
        return response.json()["status"]

    def _download(self, output_path):
        download_signed_url = self._get_download_signed_url()

        # TODO: check if output path is NULL, add user file selection

        self._update_status(Status.TRANSFERRING_TO_CLIENT.value)

        with requests.get(download_signed_url, stream=True) as r:
            r.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        self._update_status(Status.TRANSFERRED_TO_CLIENT.value)

    def _get_download_signed_url(self):
        response = requests.get(
            "/".join([self.PIPELINE_URL, self.CUSTOMER_ID, "downloads"]),
            headers=self.HEADERS,
        )
        response.raise_for_status()
        # TODO: add support for multiple download files
        return response.json()[0]["signed_url"]

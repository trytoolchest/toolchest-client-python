import time

import requests

from auth import get_key
from status import Status

class Query():
    BASE_URL = "http://toolchest.us-east-1.elasticbeanstalk.com"
    PIPELINE_ROUTE = "/pipeline-segment-instances"
    PIPELINE_URL = BASE_URL + PIPELINE_URL

    WAIT_FOR_JOB_DELAY = 15

    def run_query(self, tool_name, tool_version,
            tool_args=None, input_name=None, output_name=None,
            input_path=None, output_path=None):
        # TODO: check arguments

        key = get_key()
        self.HEADERS = {"Authorization": "Key " + key}

        create_response = self._send_initial_request(
            tool_name,
            tool_version,
            tool_args,
            input_name,
            output_name,
        )
        create_content = create_response.text
        self.CUSTOMER_ID = create_content["id"]
        self.STATUS_URL = "/".join(
            self.PIPELINE_URL,
            self.CUSTOMER_ID,
            "status",
        )
        self.UPLOAD_URL = create_content["input_file_upload_location"]

        print("Uploading...")
        self._upload(input_path)
        print("Uploaded!")

        print("Executing job...")
        self._wait_for_job(input_path)
        print("Job complete!")

        print("Downloading...")
        self._download(output_path)
        print("Downloaded!")

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
            headers=headers,
            data=open(input_path, "rb")
        )
        upload_response.raise_for_status()

        self._update_status(Status.TRANSFERRED_FROM_CLIENT.value)

    def _update_status(new_status):
        response = requests.put(
            self.STATUS_URL,
            headers=self.HEADERS,
            json={"status": new_status},
        )
        response.raise_for_status()
        return response

    def _wait_for_job(self):
        status = self._get_job_status()
        while status != Status.READY_TO_TRANSFER_TO_CLIENT.value:
            time.sleep(self.WAIT_FOR_JOB_DELAY)
            status = self._get_job_status()

    def _get_job_status(self):
        response = requests.get(
            self.STATUS_URL,
            headers=self.HEADERS
        )
        response.raise_for_status()
        return response.text["status"]

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
            "/".join(self.API_URL, self.CUSTOMER_ID, "downloads"),
            headers=self.HEADERS,
        )
        response.raise_for_status()
        # TODO: add support for multiple download files
        return response.text[0]["signed_url"]

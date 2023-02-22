"""
toolchest_client.api.query
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides a Query object to execute any queries made by Toolchest
tools. These queries are handled by the Toolchest (server) API.
"""
from loguru import logger
import os
import sys
import time
from urllib.parse import urlparse

import boto3
import requests
import docker
from requests.exceptions import HTTPError
from docker.errors import ImageNotFound, DockerException, APIError

from toolchest_client.api.auth import get_headers
from toolchest_client.api.download import download, get_download_details
from toolchest_client.api.exceptions import ToolchestJobError, ToolchestException, ToolchestDownloadError
from toolchest_client.api.output import Output
from toolchest_client.api.streaming import StreamingClient
from toolchest_client.api.urls import get_pipeline_segment_instances_url
from toolchest_client.files import OutputType, path_is_s3_uri, path_is_http_url, path_is_accessible_ftp_url
from toolchest_client.logging import get_log_level
from .instance_type import InstanceType
from .status import Status, PrettyStatus
from ..files.s3 import UploadTracker


class Query:
    """A Toolchest query.

    Provides persistence of query-specific variables from start (query
    creation) to finish (query output download).

    """

    # Period (in seconds) between requests when waiting for job(s) to finish executing.
    WAIT_FOR_JOB_DELAY = 1
    # Max number of retries on status check timeouts.
    RETRY_STATUS_CHECK_LIMIT = 5

    def __init__(self, is_async=False, pipeline_segment_instance_id=None,
                 streaming_enabled=False):
        # Configure Toolchest API authorization.
        self.headers = get_headers()

        if pipeline_segment_instance_id:
            self.pipeline_segment_instance_id = pipeline_segment_instance_id
            self.pipeline_segment_instance_url = "/".join([
                get_pipeline_segment_instances_url(),
                self.pipeline_segment_instance_id,
            ])
            self.status_url = "/".join([
                self.pipeline_segment_instance_url,
                "status",
            ])
            self.streaming_attributes_url = "/".join([
                self.pipeline_segment_instance_url,
                "output-stream",
            ])
        else:
            self.pipeline_segment_instance_id = None
            self.pipeline_segment_instance_url = None
            self.status_url = None
            self.streaming_attributes_url = None

        self.mark_as_failed = False
        self.pretty_status = None
        self.is_async = is_async

        self.status_check_retries = 0

        self.unpacked_output_file_paths = None
        self.output = Output()

        self.streaming_enabled = streaming_enabled
        self.streaming_client = StreamingClient()
        self.streaming_asyncio_task = None

    def run_query(self, tool_name, tool_version, input_prefix_mapping,
                  output_type, tool_args=None, database_name=None, database_version=None,
                  remote_database_path=None, remote_database_primary_name=None, input_files=None,
                  input_is_compressed=False, is_database_update=False, database_primary_name=None, output_path=None,
                  output_primary_name=None, skip_decompression=False, custom_docker_image_id=None,
                  instance_type=None, volume_size=None, provider="aws"):
        """Executes a query to the Toolchest API.

        :param tool_name: Tool to be used.
        :param tool_version: Version of tool to be used.
        :param tool_args: Tool-specific arguments to be passed to the tool.
        :param database_name: Name of database to be used.
        :param database_version: Version of database to be used.
        :param remote_database_path: Path (S3 URI) to a custom database.
        :param remote_database_primary_name: Primary name (i.e. common prefix) of S3 custom database.
        :param custom_docker_image_id: Image id of a custom docker image on the local machine.
        :param input_is_compressed: Whether the input file is a compressed archive of local files.
            Only used in cases where a single input is given.
        :param input_prefix_mapping: Mapping of input filepaths to associated prefix tags (e.g., "-1").
        :param is_database_update: Whether the call is to update an existing database.
        :param database_primary_name: Name of the file to use as the primary database file,
            if updating a database and uploading multiple files. If unspecified, assumes that the
            *directory* of files is the database.
        :param output_primary_name: (optional) basename of the primary output (e.g. "sample.fastq").
        :param input_files: List of paths to be passed in as input.
        :param output_path: Path to directory (client-side) where the output file(s) will be downloaded.
        :param output_type: Type (e.g. GZ_TAR) of the output file.
        :param skip_decompression: Whether to skip decompression of the output file, if it is an archive.
        :param instance_type: instance type that the tool will run on.
        :param volume_size: size of the volume for the instance.
        :param provider: where the run will happen.
        """
        self.pretty_status = ''

        # Create pipeline segment and task(s).
        # Retrieve query ID and upload URL from initial response.
        create_response = self._send_initial_request(
            compress_output=True if output_type == OutputType.GZ_TAR else False,
            database_name=database_name,
            database_version=database_version,
            remote_database_path=remote_database_path,
            remote_database_primary_name=remote_database_primary_name,
            custom_docker_image_id=custom_docker_image_id,
            is_database_update=is_database_update,
            database_primary_name=database_primary_name,
            tool_name=tool_name,
            tool_version=tool_version,
            tool_args=tool_args,
            output_file_path=output_path,
            output_primary_name=output_primary_name,
            instance_type=instance_type,
            volume_size=volume_size,
            streaming_enabled=self.streaming_enabled,
            provider=provider
        )
        create_content = create_response.json()

        self._update_pretty_status(PrettyStatus.INITIALIZED)
        self.mark_as_failed = True

        self.pipeline_segment_instance_id = create_content["id"]
        self.pipeline_segment_instance_url = "/".join([
            get_pipeline_segment_instances_url(),
            self.pipeline_segment_instance_id
        ])
        self.status_url = "/".join([
            self.pipeline_segment_instance_url,
            "status",
        ])
        self.streaming_attributes_url = "/".join([
            self.pipeline_segment_instance_url,
            "output-stream",
        ])

        self.output.set_run_id(self.pipeline_segment_instance_id)
        self.output.set_tool(
            tool_name=tool_name,
            tool_version=tool_version,
        )
        self.output.set_database(
            database_name=create_content.get("database_name"),
            database_version=create_content.get("database_version"),
        )

        self._update_pretty_status(PrettyStatus.UPLOADING)
        self._upload(input_files, input_prefix_mapping, input_is_compressed)
        self._upload_docker_image(custom_docker_image_id)
        self._update_status(Status.TRANSFERRED_FROM_CLIENT)

        self._update_pretty_status(PrettyStatus.EXECUTING)

        if self.is_async:
            return self.output

        self._wait_for_job()

        self._download(output_path, output_type, skip_decompression)

        self.mark_as_failed = False
        self._update_status(Status.COMPLETE)
        self._update_pretty_status(PrettyStatus.COMPLETE)

        self.output.set_s3_uri(self.output_s3_uri)
        self.output.set_output_path(output_path, self.unpacked_output_file_paths)
        self.output.refresh_status()
        return self.output

    def _send_initial_request(self, tool_name, tool_version, tool_args, database_name, database_version,
                              remote_database_path, remote_database_primary_name, output_primary_name, output_file_path,
                              compress_output, is_database_update, database_primary_name, custom_docker_image_id,
                              instance_type, volume_size, streaming_enabled, provider):
        """Sends the initial request to the Toolchest API to create the query.

        Returns the response from the POST request.
        """
        # Casting will check if string based requests are valid and not affect enum based ones
        validated_instance_type = None
        if instance_type is not None:
            validated_instance_type = InstanceType(instance_type).value

        create_body = {
            "compress_output": compress_output,
            "custom_tool_args": tool_args,
            "custom_database_s3_location": remote_database_path,
            "custom_database_s3_primary_name": remote_database_primary_name,
            "database_name": database_name,
            "database_version": database_version,
            "is_database_update": is_database_update,
            "database_primary_name": database_primary_name,
            "tool_name": tool_name,
            "tool_version": tool_version,
            "output_file_path": output_file_path,
            "output_file_primary_name": output_primary_name,
            "custom_docker_image_id": custom_docker_image_id,
            "instance_type": validated_instance_type,
            "volume_size": volume_size,  # API tool definitions provide a default if not set here
            "streaming_enabled": streaming_enabled,
            "provider": provider,
        }

        create_response = requests.post(
            get_pipeline_segment_instances_url(),
            headers=self.headers,
            json=create_body,
        )
        try:
            create_response.raise_for_status()
        except HTTPError:
            logger.error("Query creation failed.", file=sys.stderr)
            raise

        return create_response

    def _update_file_size(self, file_id):
        update_file_size_url = "/".join([
            get_pipeline_segment_instances_url(),
            'input-files',
            file_id,
            'update-file-size'
        ])

        response = requests.put(
            update_file_size_url,
            headers=self.headers,
        )
        try:
            response.raise_for_status()
        except HTTPError:
            logger.error(f"Failed to update size for file: {file_id}", file=sys.stderr)
            raise

    def _register_input_file(self, input_file_path, input_prefix, input_order, input_is_compressed):
        register_input_file_url = "/".join([
            self.pipeline_segment_instance_url,
            'input-files'
        ])
        file_name = os.path.basename(input_file_path)
        input_is_in_s3 = path_is_s3_uri(input_file_path)
        input_is_http_url = path_is_http_url(input_file_path)
        input_is_ftp_url = path_is_accessible_ftp_url(input_file_path)
        if input_is_http_url:
            url_path = urlparse(input_file_path).path
            file_name = os.path.basename(url_path)
        if input_is_in_s3:
            file_name = os.path.basename(input_file_path.rstrip("/"))
        response = requests.post(
            register_input_file_url,
            headers=self.headers,
            json={
                "file_name": file_name,
                "tool_prefix": input_prefix,
                "tool_prefix_order": input_order,
                "s3_uri": input_file_path if input_is_in_s3 else None,
                "http_url": input_file_path if input_is_http_url else None,
                "ftp_url": input_file_path if input_is_ftp_url else None,
                "is_compressed": input_is_compressed,
            },
        )
        try:
            response.raise_for_status()
        except HTTPError:
            logger.error(f"Failed to register input file at {input_file_path}", file=sys.stderr)
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

    def _upload(self, input_file_paths, input_prefix_mapping, input_is_compressed):
        """Uploads the files at ``input_file_paths`` to Toolchest."""

        logger.debug("Starting to upload files")
        self._update_status(Status.TRANSFERRING_FROM_CLIENT)

        for file_path in input_file_paths:
            input_is_in_s3 = path_is_s3_uri(file_path)
            input_is_http_url = path_is_http_url(file_path)
            input_is_ftp_url = path_is_accessible_ftp_url(file_path)
            input_prefix_details = input_prefix_mapping.get(file_path)
            input_prefix = input_prefix_details.get("prefix") if input_prefix_details else None
            input_order = input_prefix_details.get("order") if input_prefix_details else None
            # If the file is already in S3, there is no need to upload.
            if input_is_in_s3 or input_is_http_url or input_is_ftp_url:
                # Registers the file in the internal DB.
                self._register_input_file(
                    input_file_path=file_path,
                    input_prefix=input_prefix,
                    input_order=input_order,
                    input_is_compressed=input_is_compressed,
                )
            else:
                logger.debug(f"Uploading {file_path}")
                input_file_keys = self._register_input_file(
                    input_file_path=file_path,
                    input_prefix=input_prefix,
                    input_order=input_order,
                    input_is_compressed=input_is_compressed,
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
                        Callback=UploadTracker(file_path)
                    )
                    self._update_file_size(input_file_keys["file_id"])
                except Exception as e:
                    self._update_status_to_failed(
                        f"{e} \n\nInput file upload failed for file at {file_path}.",
                        force_raise=True
                    )
        logger.debug("Done uploading files")

    def _upload_docker_image(self, custom_docker_image_id):
        if custom_docker_image_id is None:
            return
        try:  # Try to get the image before creating a repository.
            client = docker.from_env()
            image = client.images.get(custom_docker_image_id)
        except ImageNotFound:
            return
        except (APIError, DockerException):
            logger.warning(f"Unable to find Docker running on this machine, assuming {custom_docker_image_id} "
                           "is in Dockerhub. If it's on this machine, start Docker and rerun.")
            return
        register_input_file_url = "/".join([
            self.pipeline_segment_instance_url,
            'docker-image'
        ])

        response = requests.post(
            register_input_file_url,
            headers=self.headers,
            json={
                "custom_docker_image_id": custom_docker_image_id,
            },
        )

        try:
            response.raise_for_status()
        except HTTPError:
            logger.error("Failed to create repository", file=sys.stderr)
            raise

        response_json = response.json()
        aws_info = {
            "aws_account_id": response_json.get('aws_account_id'),
            "ecr_session_password": response_json.get('ecr_password'),
            "region": response_json.get('region'),
            "repository_name": response_json.get('repository_name')
        }
        try:
            registry = f"{aws_info['aws_account_id']}.dkr.ecr.{aws_info['region']}.amazonaws.com"
            client.login(
                username="AWS",
                password=aws_info['ecr_session_password'],
                registry=registry,
            )
            docker_image_name_and_tag = custom_docker_image_id.split(':')
            docker_tag = docker_image_name_and_tag[1] if len(docker_image_name_and_tag) > 1 else 'latest'
            image_id = f"{registry}/{aws_info['repository_name']}:{docker_tag}"
            image.tag(image_id, docker_tag)
            push_output = client.api.push(
                image_id,
                tag=docker_tag,
                stream=True,
                decode=True,
            )
            counter = 0
            for update in push_output:
                if 'errorDetail' in update:
                    raise ToolchestJobError("Failed to push image.")
                # Print doesn't work on some consoles, like the JetBrains suite
                if counter % 10 == 0:
                    dots = '*' * (((counter // 10) % 10) + 1)
                    sys.stdout.write(
                        f"\rDocker image uploading ({dots})",
                    )
                    sys.stdout.flush()
                counter += 1
            logger.info("\rDocker image uploaded")
        except APIError:
            raise EnvironmentError('Unable to access ECR at this time. '
                                   'Contact Toolchest support if this error persists')

    def _update_pretty_status(self, new_status):
        """
        Updates the shared pretty status.
        """
        self.pretty_status = new_status

    def _update_status(self, new_status):
        """Updates the internal (API) status of the query's task(s).

        Returns the response from the PUT request.
        """

        response = requests.put(
            self.status_url,
            headers=self.headers,
            json={"status": new_status},
        )
        try:
            response.raise_for_status()
        except HTTPError:
            logger.error("Job status update failed.", file=sys.stderr)
            self._raise_for_failed_response(response)

        self.output.refresh_status()
        return response

    def _update_status_to_failed(self, error_message, force_raise=False, print_msg=True):
        """Updates the internal status of the query's task(s) to 'failed'.

        Includes options to print an error message or raise a ToolchestException.
        To be called when the job fails.
        """
        # Mark query as failed
        self._update_pretty_status(PrettyStatus.FAILED)

        # Mark pipeline segment instance as failed
        if self.status_url:
            requests.put(
                self.status_url,
                headers=self.headers,
                json={"status": Status.FAILED, "error_message": error_message},
            )
        self.output.refresh_status()

        self.mark_as_failed = False
        if force_raise:
            raise ToolchestException(error_message) from None
        if print_msg:
            logger.error(error_message, file=sys.stderr)

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

    def _pretty_print_query_status(self, dots):
        """Prints output of each job, supporting one query-associated job.

        Looks like: Running job (ID: 13a0f434-a19f-4a52-899a-42c85de9b97e) | Duration: 0:03:15 | Status: downloading
        """

        # The below duration is for display only, this is a hacky way to truncate the microseconds

        # Jupyter notebooks and Windows don't always support the canonical "clear-to-end-of-line" escape sequence
        max_length = 120
        status_message = f"Status: {self.pretty_status.name} ({dots}) "
        # Not using logger here, because this is analogous to a progress bar – and logger doesn't respect \r
        if get_log_level() in ["DEBUG", "INFO"]:
            sys.stdout.write(
                f"\r{status_message}".ljust(max_length),
            )
            sys.stdout.flush()

    def _wait_for_job(self):
        """Waits for query task(s) to finish executing."""
        status = self.get_job_status()
        logger.debug("Waiting for job to finish")
        counter = 0
        interval = 10
        logger.info(
            f"You can view the running job at https://dash.trytoolchest.com/runs/{self.pipeline_segment_instance_id}"
        )

        while status not in [Status.READY_TO_TRANSFER_TO_CLIENT, Status.TERMINATED, Status.COMPLETE]:
            try:
                # Set up output streaming upon transition to executing
                if status == Status.EXECUTING and self.streaming_client and not self.streaming_client.initialized:
                    self._setup_streaming()
                if self.streaming_client.ready_to_start and not self.streaming_client.stream_is_open:
                    # Clear status message before pausing
                    sys.stdout.write(
                        "\r",
                    )
                    sys.stdout.flush()
                    logger.info(
                        "Pausing job status updates soon. Will resume once standard output streaming is complete."
                    )
                    self.streaming_client.stream()
                if counter == interval - 1:
                    status_response = self.get_job_status(return_error=True)
                    status = status_response['status']
                    if status == Status.FAILED:
                        raise ToolchestJobError(status_response['error_message'])
            except TimeoutError as err:
                self.status_check_retries += 1
                if self.status_check_retries > self.RETRY_STATUS_CHECK_LIMIT:
                    raise ToolchestJobError("Status check timed out during execution, retry limit exceeded.") from err
            counter = (counter + 1) % interval
            if not self.streaming_client or not self.streaming_client.stream_is_open:
                self._pretty_print_query_status('*' * (counter + 1))
            time.sleep(self.WAIT_FOR_JOB_DELAY)
        sys.stdout.write(
            "\r",
        )
        sys.stdout.flush()
        logger.info("Run finished")

    def _download(self, output_path, output_type, skip_decompression):
        """Retrieves information needed for downloading. If ``output_path`` is given,
        downloads output to ``output_path`` and decompresses output archive, if necessary.
        """

        try:
            self.output_s3_uri, output_file_keys = get_download_details(self.pipeline_segment_instance_id)
            if output_path and not path_is_s3_uri(output_path):
                self._update_pretty_status(PrettyStatus.DOWNLOADING)
                self._update_status(Status.TRANSFERRING_TO_CLIENT)
                self.unpacked_output_file_paths = download(
                    output_path=output_path,
                    output_file_keys=output_file_keys,
                    output_type=output_type,
                    skip_decompression=skip_decompression,
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

    def get_job_status(self, return_error=False):
        """Gets status of current job (tasks)."""

        response = requests.get(
            self.status_url,
            headers=self.headers
        )
        try:
            response.raise_for_status()
        except HTTPError:
            logger.error("Job status retrieval failed.", file=sys.stderr)
            # Assumes a job has already been marked as failed if failure is detected after execution begins.
            self.mark_as_failed = False
            self._raise_for_failed_response(response)
        if return_error:
            return response.json()
        return response.json()["status"]

    def _setup_streaming(self):
        get_attrs_response = requests.get(
            self.streaming_attributes_url,
            headers=self.headers,
        )
        if get_attrs_response.ok:
            streaming_attributes = get_attrs_response.json()
            server_setup_complete = streaming_attributes.get("server_setup_complete")

            if server_setup_complete:
                self.streaming_client.initialize_params(
                    streaming_token=streaming_attributes["streaming_token"],
                    streaming_ip_address=streaming_attributes["streaming_ip_address"],
                    streaming_tls_cert=streaming_attributes["streaming_tls_cert"],
                )

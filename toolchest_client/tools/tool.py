"""
toolchest_client.tools.tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the base class from which all tools descend.
Tool must be extended by an implementation (see kraken2.py) to be functional.
"""
import asyncio
from loguru import logger
import os
import re

from toolchest_client.api.auth import validate_key
from toolchest_client.api.status import Status
from toolchest_client.api.query import Query
from toolchest_client.files import files_in_path, sanity_check, check_file_size, compress_files_in_path, OutputType
from toolchest_client.files.s3 import path_is_s3_uri
from toolchest_client.logging import setup_logging
from toolchest_client.tools.tool_args import TOOL_ARG_LISTS, VARIABLE_ARGS

FOUR_POINT_FIVE_GIGABYTES = int(4.5 * 1024 * 1024 * 1024)


class Tool:
    def __init__(self, tool_name, tool_version, tool_args,
                 inputs, min_inputs=1, max_inputs=100, output_path=None,
                 output_primary_name=None, database_name=None,
                 database_version=None, remote_database_path=None, remote_database_primary_name=None,
                 input_prefix_mapping=None, parallel_enabled=False,
                 max_input_bytes_per_file=FOUR_POINT_FIVE_GIGABYTES,
                 max_input_bytes_per_file_parallel=FOUR_POINT_FIVE_GIGABYTES,
                 group_paired_ends=False, compress_inputs=False,
                 output_type=OutputType.FLAT_TEXT, expected_output_file_names=None,
                 is_async=False, is_database_update=False, database_primary_name=None,
                 skip_decompression=False, custom_docker_image_id=None, instance_type=None,
                 volume_size=None, streaming_enabled=False, retain_base_directory=False,
                 run_location="aws", log_level=None):
        self.tool_name = tool_name
        self.tool_version = tool_version
        self.tool_args = tool_args
        self.output_path = output_path
        self.output_primary_name = output_primary_name
        if self._output_path_is_local():
            # absolutize path, expand user tilde if present
            self.output_path = os.path.abspath(os.path.expanduser(output_path))
        self.inputs = inputs if isinstance(inputs, str) else list(filter(lambda file: file is not None, inputs))
        # input_prefix_mapping is a dict in the shape of:
        # {
        #   "./path_to_file.txt": {
        #       "prefix": "-prefix",
        #       "order": 0,
        #   }
        # }
        self.input_prefix_mapping = input_prefix_mapping or dict()
        self.input_files = None
        self.num_input_files = None
        self.min_inputs = min_inputs
        self.max_inputs = max_inputs
        self.database_name = database_name
        self.database_version = database_version
        self.remote_database_path = remote_database_path
        self.remote_database_primary_name = remote_database_primary_name
        self.parallel_enabled = parallel_enabled
        self.output_validation_enabled = True
        self.group_paired_ends = group_paired_ends
        self.compress_inputs = compress_inputs
        self.max_input_bytes_per_file = max_input_bytes_per_file
        self.max_input_bytes_per_file_parallel = max_input_bytes_per_file_parallel
        self.terminating = False
        self.output_type = output_type or OutputType.FLAT_TEXT
        self.expected_output_file_names = expected_output_file_names or []
        self.is_async = is_async
        self.is_database_update = is_database_update
        self.database_primary_name = database_primary_name
        self.skip_decompression = skip_decompression
        self.custom_docker_image_id = custom_docker_image_id
        self.instance_type = instance_type
        self.volume_size = volume_size
        # auto-disable streaming if job is async
        self.streaming_enabled = False if self.is_async else streaming_enabled
        self.elapsed_seconds = 0
        self.retain_base_directory = retain_base_directory
        self.run_location = run_location
        setup_logging(log_level)

    def _prepare_inputs(self):
        """Prepares the input files."""
        if self.compress_inputs:
            self.input_files = []
            if isinstance(self.inputs, str):
                self.inputs = [self.inputs]
            for input_path in self.inputs:
                if os.path.exists(input_path):
                    # Local input files are all .tar.gz'd together, preserving directory structure
                    self.input_files += [
                        compress_files_in_path(os.path.expanduser(input_path), self.retain_base_directory)
                    ]
                else:
                    self.input_files += files_in_path(input_path)
            self.num_input_files = len(self.input_files)
        else:
            # Non compressed files are handled individually, destroying directory structure
            self.input_files = files_in_path(self.inputs)  # expands ~ in filepath if local
            self.num_input_files = len(self.input_files)

        if self.num_input_files < self.min_inputs:
            raise ValueError(f"Not enough input files submitted. "
                             f"Minimum is {self.min_inputs}, {self.num_input_files} found.")
        if self.max_inputs and self.num_input_files > self.max_inputs:
            raise ValueError(f"Too many input files submitted. "
                             f"Maximum is {self.max_inputs}, {self.num_input_files} found.")

    def _output_path_is_local(self):
        return isinstance(self.output_path, str) and not path_is_s3_uri(self.output_path)

    def _validate_tool_args(self):
        """
        Validates and sanitizes user-provided custom tool_args.

        This is processed as an argument whitelist; argument tags
        are kept only if they appear as an accepted tag. If an argument
        is not on the whitelist, an error is thrown.

        If a dangerous argument – one that changes the function or
        structure of the Toolchest run – is found, complexity is
        reduced (no validation, no parallelization) and a warning
        is shown.
        """

        tool_category = self.tool_name.replace("_parallel", "")
        whitelist = TOOL_ARG_LISTS[tool_category]["whitelist"]  # all tools have a whitelist
        dangerlist = TOOL_ARG_LISTS[tool_category].get("dangerlist", [])  # some tools have a dangerlist
        blacklist = TOOL_ARG_LISTS[tool_category].get("blacklist", [])  # some tools have a blacklist

        sanitized_args = []  # arguments that are explicitly allowed
        unknown_args = []  # all arguments that were not included
        blacklisted_args = []  # arguments that are known to not work
        dangerous_args = []  # arguments that significantly change the function of the program

        num_args_remaining_after_tag = 0

        # process arguments individually
        for arg in self.tool_args.split():
            # the minimal_tag for "--arg=a" is "--arg"
            # this allows matching args assigned via an "=" to match on the whitelist
            minimal_tag = re.sub(r"([^=]+)(=[^\s]+)", r"\1", arg)
            tag_in_whitelist = minimal_tag in whitelist
            if num_args_remaining_after_tag == 0 and tag_in_whitelist:
                # if the arg is a tag in the whitelist, add it
                sanitized_args.append(arg)
                num_args_remaining_after_tag = whitelist[minimal_tag]
                # if the arg is a tag in the dangerlist, note so can adjust accordingly
                if minimal_tag in dangerlist:
                    dangerous_args.append(arg)
            elif num_args_remaining_after_tag == VARIABLE_ARGS:
                # if previous tag has additional args (unknown/variable amount),
                # append args until another tag is found
                # TODO: filter out non-escaped bash command-line characters
                # TODO: handle variable arguments better; this allows passing of undesired args
                sanitized_args.append(arg)
                if tag_in_whitelist:
                    num_args_remaining_after_tag = whitelist[minimal_tag]
            elif num_args_remaining_after_tag > 0:
                # append remaining args if previous tag has additional args
                # TODO: filter out non-escaped bash command-line characters
                sanitized_args.append(arg)
                num_args_remaining_after_tag -= 1
            else:
                # Instead of stopping and throwing an error immediately, we wait and collect all undesired args
                if minimal_tag in blacklist:
                    blacklisted_args.append(arg)
                else:
                    unknown_args.append(arg)

        if blacklisted_args or (unknown_args and not (len(whitelist.keys()) == 1 and "*" in whitelist.keys())):
            logger.error("Non-allowed arguments found in tool_args:")
            logger.error(
                f"Blacklisted arguments (these are known to cause Toolchest to fail): \
{blacklisted_args if blacklisted_args else '(none)'}"
            )
            logger.error(
                f"Unknown arguments (these are not yet validated for use with Toolchest – please contact us!): \
{unknown_args if unknown_args else '(none)'}"
            )
            raise ValueError("Unknown or blacklisted arguments present in tool_args. See above for details.")

        # Don't change tool args with * whitelist in order to preserve ordering
        if len(whitelist.keys()) == 1 and "*" in whitelist.keys():
            return

        if dangerous_args:
            logger.warning("Dangerous arguments found in tool_args. This disables validation and parallelization!")
            logger.warning(f"Dangerous arguments: {dangerous_args}")
            # Disable parallelization, validation, and revert to plain compressed output
            self.output_validation_enabled = False
            self.parallel_enabled = False
            self.output_type = OutputType.GZ_TAR

        sanitized_args = " ".join(sanitized_args)
        if sanitized_args != self.tool_args:
            self.tool_args = sanitized_args
        logger.debug("Processing tool_args as:")
        pretty_print_args = self.tool_args if self.tool_args else "(no tool_args set)"
        logger.debug(f"\t{pretty_print_args}")

    def _validate_args(self):
        # Perform a deep tool_args validation
        # This has to happen before checking the input args, as in some cases parallelization is disabled and
        # expected input / output values may change.
        self._validate_tool_args()

        if self.inputs is None:
            raise ValueError("No input provided.")

    def _warn_if_outputs_exist(self):
        """Warns if default output files already exist in the output directory"""
        for file_path in self.expected_output_file_names + ["output", "output.tar.gz"]:
            joined_file_path = os.path.join(self.output_path, file_path)
            if os.path.exists(joined_file_path):
                logger.warning(f"{joined_file_path} already exists and will be overwritten")

    def _preflight(self):
        """Generic preflight check. Tools can have more specific implementations."""
        # Validate Toolchest auth key.
        validate_key()

        # Check if the given output_path is a directory, if required by the tool
        # and if the user provides output_path.
        if self._output_path_is_local():
            if os.path.exists(self.output_path):
                if os.path.isfile(self.output_path):
                    raise ValueError(
                        f"{self.output_path} is a file. Please pass a directory instead of an output file."
                    )
            else:
                os.makedirs(self.output_path, exist_ok=True)
            self._warn_if_outputs_exist()

        # Check if running in a Jupyter notebook and disable output streaming
        if self.streaming_enabled:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop:
                logger.info("It looks like you're using a notebook, so we've disabled output streaming. "
                            "To suppress this message, set `streaming_enabled=False`")
                self.streaming_enabled = False

    def _postflight(self, output):
        """Generic postflight check. Tools can have more specific implementations."""
        if self._output_path_is_local() and not self.is_async:
            if self.output_validation_enabled:
                # mark: quiet
                logger.debug("Checking output...")
                for output_file_name in self.expected_output_file_names:
                    output_file_path = f"{self.output_path}/{output_file_name}"
                    sanity_check(output_file_path)

    def run(self):
        """Constructs and runs a Toolchest query."""
        # mark: quiet
        logger.debug("Beginning Toolchest analysis run.")

        self._validate_args()

        # Preflight check should occur after validating args, as validation may affect the preflight check
        self._preflight()

        # Prepare input files (expand paths, compress, etc)
        self._prepare_inputs()

        logger.debug(f"Found {self.num_input_files} files to upload.")
        logger.info('Packaging and uploading run now. '
                    'This might take a while. For progress logs, set log_level="DEBUG"')

        query = Query(
            is_async=self.is_async,
            streaming_enabled=self.streaming_enabled,
        )

        for file_path in self.input_files:
            check_file_size(file_path, max_size_bytes=self.max_input_bytes_per_file)

        query_output = query.run_query(
            remote_database_path=self.remote_database_path,
            remote_database_primary_name=self.remote_database_primary_name,
            custom_docker_image_id=self.custom_docker_image_id,
            database_name=self.database_name,
            database_version=self.database_version,
            input_files=self.input_files,
            input_is_compressed=self.compress_inputs,
            input_prefix_mapping=self.input_prefix_mapping,
            instance_type=self.instance_type,
            is_database_update=self.is_database_update,
            database_primary_name=self.database_primary_name,
            output_path=self.output_path,
            output_primary_name=self.output_primary_name,
            output_type=self.output_type,
            skip_decompression=self.skip_decompression,
            tool_name=self.tool_name,
            tool_version=self.tool_version,
            tool_args=self.tool_args,
            volume_size=self.volume_size,
            run_location=self.run_location
        )

        # Check for interrupted or failed query
        # Note: if async, then the query exits at status "executing"
        success_statuses = [
            Status.AWAITING_EXECUTION,
            Status.BEGINNING_EXECUTION,
            Status.EXECUTING
        ] if self.is_async else [Status.COMPLETE]
        run_failed = query_output.last_status not in success_statuses
        if run_failed or self.terminating:
            logger.error(
                "\nToolchest run failed. "
                "For support, contact Toolchest with the error log (above) and the following details:\n\n"
                f"run_id: {query.pipeline_segment_instance_id}\n"
            )
            return query_output

        # Do basic check for completion, merge output files
        self._postflight(query_output)
        run_id = query_output.run_id
        # Print initial completion message
        if self.is_async:
            logger.info(
                f"\nAsync Toolchest initiation is complete! Your run ID is included in the returned object.\n"
                f"To check the status of this run, call toolchest.get_status(run_id=\"{run_id}\").\n"
            )
        else:
            conditional_output_msg = "and output locations are" if not self.is_database_update else "is"
            logger.debug(
                f"\nThe run is finished! The run ID {conditional_output_msg} included in the Toolchest return object.\n"
            )
        # Print details about new DB or how to download, depending on whether this is a DB update
        if self.is_database_update:
            logger.info(
                f"The parameters of your new database are:\n"
                f"\tdatabase_name: \"{query_output.database_name}\"\n"
                f"\tdatabase_version: \"{query_output.database_version}\"\n"
            )
        else:
            if self.is_async:
                logger.info(
                    f"Once it's ready to download, call toolchest.download(run_id=\"{run_id}\", ...) "
                    "within 7 days\n"
                )
            else:
                logger.debug(f"To re-download the results, run toolchest.download(run_id=\"{run_id}\") within 7 days\n")

        return query_output

"""
toolchest_client.tools.tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the base class from which all tools descend.
Tool must be extended by an implementation (see kraken2.py) to be functional.
"""
import asyncio
import copy
import datetime
import os
import re
import signal
import sys
from threading import Thread
import time

from toolchest_client.api.auth import validate_key
from toolchest_client.api.exceptions import ToolchestException
from toolchest_client.api.output import Output
from toolchest_client.api.status import ThreadStatus
from toolchest_client.api.streaming import StreamingClient
from toolchest_client.api.query import Query
from toolchest_client.files import files_in_path, split_file_by_lines, sanity_check, check_file_size, \
    split_paired_files_by_lines, compress_files_in_path, OutputType
from toolchest_client.files.s3 import inputs_are_in_s3, path_is_s3_uri
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
                 skip_decompression=False, custom_docker_image_id=None,
                 instance_type=None, volume_size=None, streaming_enabled=False):
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
        self.query_threads = []
        self.query_thread_statuses = dict()
        self.terminating = False
        self.output_type = output_type or OutputType.FLAT_TEXT
        self.thread_outputs = {}
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
        self.streaming_client = None
        self.streaming_asyncio_task = None
        self.elapsed_seconds = 0
        signal.signal(signal.SIGTERM, self._handle_termination)
        signal.signal(signal.SIGINT, self._handle_termination)

    def _prepare_inputs(self):
        """Prepares the input files."""
        if self.compress_inputs:
            self.input_files = []
            if isinstance(self.inputs, str):
                self.inputs = [self.inputs]
            for input_path in self.inputs:
                if path_is_s3_uri(input_path):
                    # If the given path is in S3, it does not require compression.
                    self.input_files += [files_in_path(input_path)]
                    # self.compress_inputs = False
                elif os.path.isfile(input_path):
                    self.input_files += [input_path]
                else:
                    # Input files are all .tar.gz'd together, preserving directory structure
                    self.input_files += [compress_files_in_path(os.path.expanduser(input_path))]
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
            print("Non-allowed arguments found in tool_args:")
            print(
                f"Blacklisted arguments (these are known to cause Toolchest to fail): \
{blacklisted_args if blacklisted_args else '(none)'}"
            )
            print(
                f"Unknown arguments (these are not yet validated for use with Toolchest – please contact us!): \
{unknown_args if unknown_args else '(none)'}"
            )
            raise ValueError("Unknown or blacklisted arguments present in tool_args. See above for details.")

        # Don't change tool args with * whitelist in order to preserve ordering
        if len(whitelist.keys()) == 1 and "*" in whitelist.keys():
            return

        if dangerous_args:
            print("WARNING: dangerous arguments found in tool_args. This disables validation and parallelization!")
            print(f"Dangerous arguments: {dangerous_args}")
            # Disable parallelization, validation, and revert to plain compressed output
            self.output_validation_enabled = False
            self.parallel_enabled = False
            self.output_type = OutputType.GZ_TAR

        sanitized_args = " ".join(sanitized_args)
        if sanitized_args != self.tool_args:
            self.tool_args = sanitized_args
        print("Processing tool_args as:")
        pretty_print_args = self.tool_args if self.tool_args else "(no tool_args set)"
        print(f"\t{pretty_print_args}")

    def _validate_args(self):
        # Perform a deep tool_args validation
        # This has to happen before checking the input args, as in some cases parallelization is disabled and
        # expected input / output values may change.
        self._validate_tool_args()

        if self.inputs is None:
            raise ValueError("No input provided.")

    def _merge_outputs(self, output_file_paths):
        """Merges output files for parallel runs."""
        raise NotImplementedError(f"Merging outputs not enabled for this tool {self.tool_name}")

    def _warn_if_outputs_exist(self):
        """Warns if default output files already exist in the output directory"""
        for file_path in self.expected_output_file_names + ["output", "output.tar.gz"]:
            joined_file_path = os.path.join(self.output_path, file_path)
            if os.path.exists(joined_file_path):
                print(f"WARNING: {joined_file_path} already exists and will be overwritten")

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

    def _postflight(self, output):
        """Generic postflight check. Tools can have more specific implementations."""
        if self._output_path_is_local() and not self.is_async:
            if self.output_validation_enabled:
                print("Checking output...")
                for output_file_name in self.expected_output_file_names:
                    output_file_path = f"{self.output_path}/{output_file_name}"
                    sanity_check(output_file_path)

    def _system_supports_parallel_execution(self):
        """Checks if parallel execution is supported on the platform.

        Right now, this blindly rejects anything other than Linux or macOS.
        Windows is not currently supported, because pysam requires htslib
        """
        if sys.platform not in {'linux', 'darwin'}:
            raise NotImplementedError(f"Parallel execution is not yet supported for your OS: {sys.platform}")
        return True

    def _pretty_print_pipeline_segment_status(self):
        """Prints output of each job, supporting multiple simultaneous jobs.

        Looks like: Running 2 jobs | Duration: 0:03:15 | 1 jobs complete | 1 jobs downloading
        """
        status_counts = {}
        for thread_name, thread_status in self.query_thread_statuses.items():
            if status_counts.get(thread_status):
                status_counts[thread_status] = status_counts[thread_status] + 1
            else:
                status_counts[thread_status] = 1

        job_or_jobs = "job" if len(self.query_threads) == 1 else "jobs"
        status_count = ""
        for status_name in status_counts:
            status_count += f"| {status_counts[status_name]} {job_or_jobs} {status_name} "

        job_count = f"Running {len(self.query_threads)} {job_or_jobs}"
        jobs_duration = f"Duration: {str(datetime.timedelta(seconds=self.elapsed_seconds))}"

        # Jupyter notebooks and Windows don't always support the canonical "clear-to-end-of-line" escape sequence
        max_length = 120
        status_message = f"\r{job_count} | {jobs_duration} {status_count}"
        print(f"{status_message}".ljust(max_length), end="\r")

    def _handle_termination(self, signal_number, *_):
        """
        Handles termination by killing threads and stopping the output stream.

        If two signals are received in a row (e.g. two ctrl-c's), raises an error without killing threads.
        """
        if self.terminating:
            raise InterruptedError("Toolchest client force killed")
        self.terminating = True
        if self.streaming_asyncio_task and not self.streaming_asyncio_task.done():
            self.streaming_asyncio_task.cancel()
        self._kill_query_threads()
        raise InterruptedError(f"Toolchest client interrupted by signal #{signal_number}")

    def _kill_query_threads(self):
        """
        Sends a signal to threads to terminate.

        Query threads occasionally check the flag for termination, so they may take a while to terminate.
        """
        for thread in self.query_threads:
            thread_name = thread.getName()
            thread_status = self.query_thread_statuses.get(thread_name)
            if thread.is_alive() and thread_status not in {ThreadStatus.COMPLETE, ThreadStatus.FAILED}:
                self.query_thread_statuses[thread_name] = ThreadStatus.INTERRUPTING

        # Wait for remaining threads to finish terminating
        increment_seconds = 5
        for thread in self.query_threads:
            while thread.is_alive():
                self._pretty_print_pipeline_segment_status()
                self.elapsed_seconds += increment_seconds
                time.sleep(increment_seconds)
        for thread in self.query_threads:
            thread.join()

    def _check_thread_health(self):
        """Checks for any thread that has ended without reaching a "success" state, and propagates errors"""
        for thread in self.query_threads:
            thread_name = thread.getName()
            thread_status = self.query_thread_statuses.get(thread_name)
            success_status = ThreadStatus.EXECUTING if self.is_async else ThreadStatus.COMPLETE
            if not thread.is_alive() and thread_status != success_status:
                self._kill_query_threads()
                raise ToolchestException("A job irrecoverably failed. See logs above for details.")

    def _start_or_check_stream(self):
        # Start streaming (in place of regular status updates).
        if not self.streaming_asyncio_task:
            # Clear the last status line before streaming begins
            print("".ljust(120), end="\r")
            self.streaming_asyncio_task = asyncio.create_task(self.streaming_client.receive_stream())
        # Check if an exception was raised in the streaming task
        elif self.streaming_asyncio_task.done() and self.streaming_asyncio_task.exception():
            self._kill_query_threads()
            error_message = (
                "An error was encountered during output streaming. See logs above for details."
            )
            raise ToolchestException(error_message) from self.streaming_asyncio_task.exception()

    async def _wait_for_threads_to_finish(self):
        """Waits for all jobs and their corresponding threads to finish while printing their statuses
        or streaming thread output, if enabled."""
        # Wait for all threads to finish uploading
        self._wait_for_threads_to_upload()

        for thread in self.query_threads:
            increment_seconds = 5
            while thread.is_alive():
                self._check_thread_health()

                if self.streaming_enabled and self.streaming_client.initialized:
                    self._start_or_check_stream()
                else:
                    self._pretty_print_pipeline_segment_status()

                self.elapsed_seconds += increment_seconds
                await asyncio.sleep(increment_seconds)

            # Wait for the stream to complete before printing final status line
            if self.streaming_asyncio_task:
                await self.streaming_asyncio_task

            thread_name = thread.getName()
            thread_final_status = self.query_thread_statuses.get(thread_name)
            if thread_final_status == ThreadStatus.COMPLETE:
                self._pretty_print_pipeline_segment_status()
        print("")

        # Double check all threads are complete for safety
        for thread in self.query_threads:
            thread.join()

    def _wait_for_threads_to_upload(self):
        """Waits for all jobs to finish uploading. To be used only at the start of a run."""
        uploading = True
        while uploading:
            # Verify that all threads are healthy while uploading
            self._check_thread_health()

            statuses = []
            for thread in self.query_threads:
                thread_name = thread.getName()
                statuses.append(self.query_thread_statuses.get(thread_name))
            uploading = any(
                map(lambda status: status in [ThreadStatus.INITIALIZING, ThreadStatus.INITIALIZED,
                                              ThreadStatus.UPLOADING], statuses)
            )
            if uploading:
                time.sleep(5)

    def _generate_jobs(self, should_run_in_parallel):
        """Generates staggered jobs for both parallel and non-parallel runs.

        Each job is simply an array containing the input file paths for the job, as the rest
        of the context is shared amongst jobs (e.g. tool, database, prefix mapping, etc.).

        Note that this is a generator.
        """

        if should_run_in_parallel:
            if not self.group_paired_ends:
                # Arbitrary parallelization – assume only one input file which is to be split
                adjusted_input_file_paths = split_file_by_lines(
                    input_file_path=self.input_files[0],
                    max_bytes=self.max_input_bytes_per_file_parallel,
                )
                for _, file_path in adjusted_input_file_paths:
                    # This is assuming only one input file per parallel run.
                    # This will need to be changed once we support multiple input files for parallelization.
                    yield [file_path]
            else:
                # Grouped parallelization. Right now, this only supports grouping by R1/R2 for paired-end inputs
                input_file_paths_pairs = split_paired_files_by_lines(
                    input_file_paths=self.input_files,
                    max_bytes=self.max_input_bytes_per_file_parallel,
                )
                for input_file_path_pair in input_file_paths_pairs:
                    yield input_file_path_pair

        else:
            # Make sure we're below tool limit for non-splittable files
            for file_path in self.input_files:
                check_file_size(file_path, max_size_bytes=self.max_input_bytes_per_file)
            # Note that for a tool like Unicycler, this would look like:
            # [["r1.fastq", "r2.fastq", "unassembled.fasta"]]
            # As there are multiple input files required for the job
            yield self.input_files

    def run(self):
        """Constructs and runs a Toolchest query."""
        print("Beginning Toolchest analysis run.")

        # todo: better propagate and handle errors for parallel runs
        self._validate_args()

        # Preflight check should occur after validating args, as validation may affect the preflight check
        self._preflight()

        # Prepare input files (expand paths, compress, etc)
        self._prepare_inputs()

        print(f"Found {self.num_input_files} files to upload.")

        if self.streaming_enabled:
            self.streaming_client = StreamingClient()

        should_run_in_parallel = self.parallel_enabled \
            and not any(inputs_are_in_s3(self.input_files)) \
            and (self.group_paired_ends or self.num_input_files == 1) \
            and self._system_supports_parallel_execution()

        if should_run_in_parallel and self.is_async:
            print("WARNING: Disabling async execution for parallel run. This run will be synchronous.")
            self.is_async = False

        jobs = self._generate_jobs(should_run_in_parallel)

        # Set up the individual queries for parallelization
        # Note that this is relying on a result from the generator, so these are slightly staggered
        temp_input_file_paths = []
        temp_output_file_paths = []
        non_parallel_output_path = self.output_path
        for thread_index, input_files in enumerate(jobs):
            # Add split files for merging and later deletion, if running in parallel
            # TODO: handle parallel output for s3 uri
            temp_parallel_output_file_path = f"{self.output_path}_{thread_index}"
            if should_run_in_parallel:
                temp_input_file_paths += input_files
                temp_output_file_paths.append(temp_parallel_output_file_path)

            # Create a new Output for the thread.
            self.thread_outputs[thread_index] = Output()
            q = Query(
                stored_output=self.thread_outputs[thread_index],
                is_async=self.is_async,
                streaming_enabled=self.streaming_enabled,
                streaming_client=self.streaming_client,
            )

            # Deep copy to make thread safe
            # Note: multithreaded download may be broken with output_path refactor
            query_args = copy.deepcopy({
                "remote_database_path": self.remote_database_path,
                "remote_database_primary_name": self.remote_database_primary_name,
                "custom_docker_image_id": self.custom_docker_image_id,
                "database_name": self.database_name,
                "database_version": self.database_version,
                "input_files": input_files,
                "input_is_compressed": self.compress_inputs,
                "input_prefix_mapping": self.input_prefix_mapping,
                "instance_type": self.instance_type,
                "is_database_update": self.is_database_update,
                "database_primary_name": self.database_primary_name,
                "output_path": temp_parallel_output_file_path if should_run_in_parallel else non_parallel_output_path,
                "output_primary_name": self.output_primary_name,
                "output_type": self.output_type,
                "skip_decompression": self.skip_decompression,
                "tool_name": self.tool_name,
                "tool_version": self.tool_version,
                "tool_args": self.tool_args,
                "volume_size": self.volume_size
            })

            # Add non-distinct dictionary for status updates
            query_args["thread_statuses"] = self.query_thread_statuses

            new_thread = Thread(target=q.run_query, kwargs=query_args)
            self.query_threads.append(new_thread)
            self.query_thread_statuses[new_thread.getName()] = ThreadStatus.INITIALIZING

            new_thread.start()

        asyncio.run(self._wait_for_threads_to_finish())

        # Check for interrupted or failed threads
        # Note: if async, then the query exits at thread status "executing"
        success_status = ThreadStatus.EXECUTING if self.is_async else ThreadStatus.COMPLETE
        run_failed = not all(status == success_status for status in self.query_thread_statuses.values())
        if run_failed or self.terminating:
            run_ids = [thread_output.run_id for thread_output in self.thread_outputs.values()]
            # Prints each run_id to a new line, surrounded by quotes, prefaced by tab
            pretty_print_run_ids = '\t\"' + '\"\n\t\"'.join(run_ids) + '\"'
            print(
                "\nToolchest run failed. "
                "For support, contact Toolchest with the error log (above) and the following details:\n\n"
                f"run_id: {pretty_print_run_ids}\n"
            )
            if not should_run_in_parallel:
                return self.thread_outputs[0]
            return

        # Do basic check for completion, merge output files, delete temporary files
        if should_run_in_parallel:
            for temp_parallel_output_file_path in temp_output_file_paths:
                sanity_check(temp_parallel_output_file_path)
            print(f"Merging {len(temp_output_file_paths)} output files...")
            self._merge_outputs(temp_output_file_paths)
            print("Merging of files complete.")
            print("Deleting temporary files...")
            temporary_file_paths = temp_input_file_paths + temp_output_file_paths
            for temporary_file_path in temporary_file_paths:
                print(f"Deleting {temporary_file_path}...")
                os.remove(temporary_file_path)
            print("Temporary files deleted.")
        else:
            self._postflight(self.thread_outputs[0])
            run_id = self.thread_outputs[0].run_id
            # Print initial completion message
            if self.is_async:
                print(
                    f"\nAsync Toolchest initiation is complete! Your run ID is included in the returned object.\n"
                    f"To check the status of this run, call toolchest.get_status(run_id=\"{run_id}\").\n"
                )
            else:
                conditional_output_msg = "and output locations are" if not self.is_database_update else "is"
                print(
                    f"\nYour Toolchest run is complete! The run ID {conditional_output_msg} included in the return.\n"
                )
            # Print details about new DB or how to download, depending on whether this is a DB update
            if self.is_database_update:
                print(
                    f"The parameters of your new database are:\n"
                    f"\tdatabase_name: \"{self.thread_outputs[0].database_name}\"\n"
                    f"\tdatabase_version: \"{self.thread_outputs[0].database_version}\"\n"
                )
            else:
                if self.is_async:
                    print(
                        f"Once it's ready to download, call toolchest.download(run_id=\"{run_id}\", ...) "
                        "within 7 days\n"
                    )
                else:
                    print(f"To re-download the results, run toolchest.download(run_id=\"{run_id}\") within 7 days\n")

        # Note: output information is only returned if parallelization is disabled
        if not should_run_in_parallel:
            return self.thread_outputs[0]

"""
toolchest_client.tools.tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the base class from which all tools descend.
Tool must be extended by an implementation (see kraken2.py) to be functional.
"""
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
from toolchest_client.api.status import ThreadStatus
from toolchest_client.api.query import Query
from toolchest_client.files import files_in_path, split_file_by_lines, sanity_check, check_file_size,\
    split_paired_files_by_lines, compress_files_in_path, OutputType
from toolchest_client.tools.arg_whitelist import ARGUMENT_WHITELIST, VARIABLE_ARGS

FOUR_POINT_FIVE_GIGABYTES = 4.5 * 1024 * 1024 * 1024


class Tool:
    def __init__(self, tool_name, tool_version, tool_args, output_name,
                 output_path, inputs, min_inputs, max_inputs,
                 database_name=None, database_version=None,
                 input_prefix_mapping=None, parallel_enabled=False,
                 max_input_bytes_per_node=FOUR_POINT_FIVE_GIGABYTES,
                 group_paired_ends=False, compress_inputs=False,
                 output_type=OutputType.FLAT_TEXT, output_is_directory=False):
        self.tool_name = tool_name
        self.tool_version = tool_version
        self.tool_args = tool_args
        self.output_name = output_name
        self.output_path = output_path
        self.output_is_directory = output_is_directory
        self.inputs = inputs
        # input_prefix_mapping is a dict in the shape of:
        # {
        #   "./path_to_file.txt": "-prefix",
        # }
        self.input_prefix_mapping = input_prefix_mapping or dict()
        self.input_files = None
        self.inputs_are_in_s3 = []
        self.num_input_files = None
        self.min_inputs = min_inputs
        self.max_inputs = max_inputs
        self.database_name = database_name
        self.database_version = database_version
        self.parallel_enabled = parallel_enabled
        self.group_paired_ends = group_paired_ends
        self.compress_inputs = compress_inputs
        self.max_input_bytes_per_node = max_input_bytes_per_node
        self.query_threads = []
        self.query_thread_statuses = dict()
        self.terminating = False
        self.output_type = output_type
        signal.signal(signal.SIGTERM, self._handle_termination)
        signal.signal(signal.SIGINT, self._handle_termination)

    def _prepare_inputs(self):
        """Prepares the input files."""
        if self.compress_inputs:
            # Input files are all .tar.gz'd together, preserving directory structure
            self.input_files = [compress_files_in_path(self.inputs)]
            self.num_input_files = 1
        else:
            # Input files are handled individually, destroying directory structure
            self.input_files = files_in_path(self.inputs)
            self.num_input_files = len(self.input_files)

        # Sanitize valid paths and list all files in self.inputs.
        self.input_files = files_in_path(self.inputs)

        # Note which files are S3 URIs.
        S3_PREFIX = "s3://"
        self.inputs_are_in_s3 = [file_path.startswith(S3_PREFIX) for file_path in self.input_files]

        self.num_input_files = len(self.input_files)
        if self.num_input_files < self.min_inputs:
            raise ValueError(f"Not enough input files submitted. "
                             f"Minimum is {self.min_inputs}, {self.num_input_files} found.")
        if self.num_input_files > self.max_inputs:
            raise ValueError(f"Too many input files submitted. "
                             f"Maximum is {self.max_inputs}, {self.num_input_files} found.")

    def _validate_args(self):
        """Validates args set by tools."""

        if self.inputs is None:
            raise ValueError("No input provided.")
        if self.output_path is None:
            raise ValueError("No output path provided.")
        if not os.access(
                os.path.dirname(self.output_path),
                os.W_OK | os.X_OK,
        ):
            raise OSError("Output file path must be writable.")
        if not self.output_name:
            raise ValueError("Output name must be non-empty.")
        if self.output_is_directory and not os.path.isdir(self.output_path):
            raise ValueError(f"Output path must be a directory. It is currently {self.output_path}")

        # Perform a deeper tool_args validation
        self._validate_tool_args()

    def _validate_tool_args(self):
        """Validates and sanitizes user-provided custom tool_args.

        Currently, this is processed as an argument whitelist; argument tags
        are kept only if they appear as an accepted tag.
        """

        tool_arg_whitelist = ARGUMENT_WHITELIST[self.tool_name]

        sanitized_args_list = []
        num_args_remaining_after_tag = 0

        # process arguments individually
        for arg in self.tool_args.split():
            # the minimal_tag for "--arg=a" is "--arg"
            # this allows matching args assigned via an "=" to match on the whitelist
            minimal_tag = re.sub(r"([^=]+)(=[^\s]+)", rf"\1", arg)
            tag_in_whitelist = minimal_tag in tool_arg_whitelist
            if num_args_remaining_after_tag == 0 and tag_in_whitelist:
                # if the arg is a tag in the whitelist, add it
                sanitized_args_list.append(arg)
                num_args_remaining_after_tag = tool_arg_whitelist[minimal_tag]
            elif num_args_remaining_after_tag == VARIABLE_ARGS:
                # if previous tag has additional args (unknown/variable amount),
                # append args until another tag is found
                # TODO: filter out non-escaped bash command-line characters
                # TODO: handle variable arguments better; this allows passing of undesired args
                sanitized_args_list.append(arg)
                if tag_in_whitelist:
                    num_args_remaining_after_tag = tool_arg_whitelist[minimal_tag]
            elif num_args_remaining_after_tag > 0:
                # append remaining args if previous tag has additional args
                # TODO: filter out non-escaped bash command-line characters
                sanitized_args_list.append(arg)
                num_args_remaining_after_tag -= 1
            # if no tag found, skip args until a tag is found

        sanitized_args = " ".join(sanitized_args_list)
        if sanitized_args != self.tool_args:
            self.tool_args = sanitized_args
        print("Processing tool_args as:")
        pretty_print_args = self.tool_args if self.tool_args else "(no tool_args set)"
        print(f"\t{pretty_print_args}")

    def _merge_outputs(self, output_file_paths):
        """Merges output files for parallel runs."""
        raise NotImplementedError(f"Merging outputs not enabled for this tool {self.tool_name}")

    def _preflight(self):
        """Generic preflight check. Tools can have more specific implementations."""
        # Validate Toolchest auth key.
        validate_key()

    def _postflight(self):
        """Generic postflight check. Tools can have more specific implementations."""
        sanity_check(self.output_path)

    def _system_supports_parallel_execution(self):
        """Checks if parallel execution is supported on the platform.

        Right now, this blindly rejects anything other than Linux or macOS.
        Windows is not currently supported, because pysam requires htslib
        """
        if sys.platform not in {'linux', 'darwin'}:
            raise NotImplementedError(f"Parallel execution is not yet supported for your OS: {sys.platform}")
        return True

    def _pretty_print_pipeline_segment_status(self, elapsed_seconds):
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
        jobs_duration = f"Duration: {str(datetime.timedelta(seconds=elapsed_seconds))}"

        # Jupyter notebooks and Windows don't always support the canonical "clear-to-end-of-line" escape sequence
        max_length = 120
        status_message = f"\r{job_count} | {jobs_duration} {status_count}"
        print(f"{status_message}{(max_length - len(status_message)) * ' '}", end="\r")

    def _handle_termination(self, signal_number, *_):
        """
        Handles termination by killing threads.

        If two signals are received in a row (e.g. two ctrl-c's), raises an error without killing threads.
        """
        if self.terminating:
            raise InterruptedError(f"Toolchest client force killed")
        self.terminating = True
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

        self._wait_for_threads_to_finish(check_health=False)

    def _check_thread_health(self):
        """Checks for any thread that has ended without reaching a "complete" state, and propagates errors"""
        for thread in self.query_threads:
            thread_name = thread.getName()
            thread_status = self.query_thread_statuses.get(thread_name)
            if not thread.is_alive() and thread_status != ThreadStatus.COMPLETE:
                self._kill_query_threads()
                raise ToolchestException(f"A job irrecoverably failed. See logs above for details.")

    def _wait_for_threads_to_finish(self, check_health=True):
        """Waits for all jobs and their corresponding threads to finish while printing their statuses."""
        elapsed_seconds = 0
        for thread in self.query_threads:
            increment_seconds = 5
            while thread.is_alive():
                if check_health:
                    self._check_thread_health()
                self._pretty_print_pipeline_segment_status(elapsed_seconds)
                elapsed_seconds += increment_seconds
                time.sleep(increment_seconds)
            self._pretty_print_pipeline_segment_status(elapsed_seconds)
        print("")

        # Double check all threads are complete for safety
        for thread in self.query_threads:
            thread.join()

    def _generate_jobs(self, should_run_in_parallel):
        """Generates staggered jobs for both parallel and non-parallel runs.

        Each job is simply an array containing the input file paths for the job, as the rest
        of the context is shared amongst jobs (e.g. tool, database, prefix mapping, etc.).

        Returns (file_path, file_is_in_s3) pairs.

        Note that this is a generator.
        """

        if should_run_in_parallel:
            PARALLEL_FILE_IS_IN_S3 = False  # S3 files are currently not parallelized.
            if not self.group_paired_ends:
                # Arbitrary parallelization – assume only one input file which is to be split
                adjusted_input_file_paths = split_file_by_lines(
                    input_file_path=self.input_files[0],
                    max_bytes=self.max_input_bytes_per_node,
                )
                for _, file_path in adjusted_input_file_paths:
                    # This is assuming only one input file per parallel run.
                    # This will need to be changed once we support multiple input files for parallelization.
                    yield [file_path, PARALLEL_FILE_IS_IN_S3]
            else:
                # Grouped parallelization. Right now, this only supports grouping by R1/R2 for paired-end inputs
                input_file_paths_pairs = split_paired_files_by_lines(
                    input_file_paths=self.input_files,
                    max_bytes=self.max_input_bytes_per_node,
                )
                for input_file_path_pair in input_file_paths_pairs:
                    yield input_file_path_pair, PARALLEL_FILE_IS_IN_S3

        else:
            # Make sure we're below plan/multi-part limit for non-splittable files
            # NOTE: If the file is already in S3, the size is checked as well to enforce an expected file size
            for file_path, file_is_in_s3 in zip(self.input_files, self.inputs_are_in_s3):
                check_file_size(file_path, max_size_bytes=FOUR_POINT_FIVE_GIGABYTES, file_is_in_s3=file_is_in_s3)
            # Note that for a tool like Unicycler, this would look like:
            # [["r1.fastq", "r2.fastq", "unassembled.fasta"]]
            # As there are multiple input files required for the job
            yield self.input_files, self.inputs_are_in_s3

    def run(self):
        """Constructs and runs a Toolchest query."""
        print("Beginning Toolchest analysis run.")

        self._preflight()

        # todo: better propagate and handle errors for parallel runs
        self._validate_args()
        # Prepare input files (expand paths, compress, etc)
        self._prepare_inputs()

        print(f"Found {self.num_input_files} files to upload.")

        # Note: if any S3 input is present, parallelization is disabled
        should_run_in_parallel = self.parallel_enabled \
            and not any(self.inputs_are_in_s3) \
            and (self.group_paired_ends or self.num_input_files == 1) \
            and check_file_size(self.input_files[0]) > self.max_input_bytes_per_node \
            and self._system_supports_parallel_execution()

        jobs = self._generate_jobs(should_run_in_parallel)

        # Set up the individual queries for parallelization
        # Note that this is relying on a result from the generator, so these are slightly staggered
        temp_input_file_paths = []
        temp_output_file_paths = []
        non_parallel_output_path = f"{self.output_path}/{self.output_name}" if self.output_is_directory \
            else self.output_path
        for index, (input_files, inputs_are_in_s3) in enumerate(jobs):
            # Add split files for merging and later deletion, if running in parallel
            temp_parallel_output_file_path = f"{self.output_path}_{index}"
            if should_run_in_parallel:
                temp_input_file_paths += input_files
                temp_output_file_paths.append(temp_parallel_output_file_path)
            q = Query()

            # Deep copy to make thread safe
            query_args = copy.deepcopy({
                "tool_name": self.tool_name,
                "tool_version": self.tool_version,
                "tool_args": self.tool_args,
                "database_name": self.database_name,
                "database_version": self.database_version,
                "output_name": f"{index}_{self.output_name}" if should_run_in_parallel else self.output_name,
                "input_files": input_files,
                "inputs_are_in_s3": inputs_are_in_s3,
                "input_prefix_mapping": self.input_prefix_mapping,
                "output_path": temp_parallel_output_file_path if should_run_in_parallel else non_parallel_output_path,
                "output_type": self.output_type,
            })

            # Add non-distinct dictionary for status updates
            query_args["thread_statuses"] = self.query_thread_statuses

            new_thread = Thread(target=q.run_query, kwargs=query_args)
            self.query_threads.append(new_thread)

            print(f"Spawning job #{len(self.query_threads)}...")
            new_thread.start()
            time.sleep(5)

        print(f"Finished spawning jobs.")

        self._wait_for_threads_to_finish()

        print("Finished execution of parallel segments. Checking output...")

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
            self._postflight()

        print("Analysis run complete!")

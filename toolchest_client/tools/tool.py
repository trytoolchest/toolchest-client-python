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
    split_paired_files_by_lines, compress_files_in_path, OutputType, assert_exists
from toolchest_client.files.s3 import inputs_are_in_s3
from toolchest_client.tools.tool_args import TOOL_ARG_LISTS, VARIABLE_ARGS

FOUR_POINT_FIVE_GIGABYTES = int(4.5 * 1024 * 1024 * 1024)


class Tool:
    def __init__(self, tool_name, tool_version, tool_args, output_name,
                 output_path, inputs, min_inputs, max_inputs,
                 database_name=None, database_version=None,
                 input_prefix_mapping=None, parallel_enabled=False,
                 max_input_bytes_per_file=FOUR_POINT_FIVE_GIGABYTES,
                 max_input_bytes_per_file_parallel=FOUR_POINT_FIVE_GIGABYTES,
                 group_paired_ends=False, compress_inputs=False,
                 output_type=OutputType.FLAT_TEXT, output_is_directory=False,
                 output_names=None):
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
        self.num_input_files = None
        self.min_inputs = min_inputs
        self.max_inputs = max_inputs
        self.database_name = database_name
        self.database_version = database_version
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
        self.output_names = output_names or []
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

        if self.num_input_files < self.min_inputs:
            raise ValueError(f"Not enough input files submitted. "
                             f"Minimum is {self.min_inputs}, {self.num_input_files} found.")
        if self.num_input_files > self.max_inputs:
            raise ValueError(f"Too many input files submitted. "
                             f"Maximum is {self.max_inputs}, {self.num_input_files} found.")

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

        whitelist = TOOL_ARG_LISTS[self.tool_name]["whitelist"]  # all tools have a whitelist
        dangerlist = TOOL_ARG_LISTS[self.tool_name].get("dangerlist", [])  # some tools have a dangerlist
        blacklist = TOOL_ARG_LISTS[self.tool_name].get("blacklist", [])  # some tools have a blacklist

        sanitized_args = []  # arguments that are explicitly allowed
        unknown_args = []  # all arguments that were not included
        blacklisted_args = []  # arguments that are known to not work
        dangerous_args = []  # arguments that significantly change the function of the program

        num_args_remaining_after_tag = 0

        # process arguments individually
        for arg in self.tool_args.split():
            # the minimal_tag for "--arg=a" is "--arg"
            # this allows matching args assigned via an "=" to match on the whitelist
            minimal_tag = re.sub(r"([^=]+)(=[^\s]+)", rf"\1", arg)
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

        if unknown_args or blacklisted_args:
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

        if dangerous_args:
            print("WARNING: dangerous arguments found in tool_args. This disables validation and parallelization!")
            print(f"Dangerous arguments: {dangerous_args}")
            # Disable parallelization, validation, and revert to plain compressed output
            self.output_validation_enabled = False
            self.parallel_enabled = False
            self.output_is_directory = True
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

    def _merge_outputs(self, output_file_paths):
        """Merges output files for parallel runs."""
        raise NotImplementedError(f"Merging outputs not enabled for this tool {self.tool_name}")

    def _warn_if_outputs_exist(self):
        """Warns if default output files already exist in the output directory"""
        for file_path in self.output_names + ["output", "output.tar.gz"]:
            joined_file_path = os.path.join(self.output_path, file_path)
            if os.path.exists(joined_file_path):
                print(f"WARNING: {joined_file_path} already exists and will be overwritten")

    def _preflight(self):
        """Generic preflight check. Tools can have more specific implementations."""
        # Validate Toolchest auth key.
        validate_key()

        if self.output_is_directory:
            if os.path.exists(self.output_path):
                if os.path.isfile(self.output_path):
                    raise ValueError(
                        f"{self.output_path} is a file. Please pass a directory instead of an output file."
                    )
            else:
                os.makedirs(self.output_path)

        self._warn_if_outputs_exist()

    def _postflight(self):
        """Generic postflight check. Tools can have more specific implementations."""
        if self.output_validation_enabled:
            for output_name in self.output_names:
                output_file_path = f"{self.output_path}/{output_name}"
                assert_exists(output_file_path, must_be_file=True)
                if os.stat(output_file_path).st_size <= 5:
                    raise ValueError(f"Output file at {output_file_path} is suspiciously small")

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

        should_run_in_parallel = self.parallel_enabled \
            and not any(inputs_are_in_s3(self.input_files)) \
            and (self.group_paired_ends or self.num_input_files == 1) \
            and self._system_supports_parallel_execution()

        jobs = self._generate_jobs(should_run_in_parallel)

        # Set up the individual queries for parallelization
        # Note that this is relying on a result from the generator, so these are slightly staggered
        temp_input_file_paths = []
        temp_output_file_paths = []
        non_parallel_output_path = f"{self.output_path}/{self.output_name}" if self.output_is_directory \
            else self.output_path
        for index, input_files in enumerate(jobs):
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

"""
toolchest_client.tools.tool
~~~~~~~~~~~~~~~~~~~~~~

This is the base class from which all tools descend.
Tool must be extended by an implementation (see kraken2.py) to be functional.
"""
import copy
import datetime
import os
from threading import Thread
import time

from ..query import Query
from ..files import files_in_path, split_file_by_lines, sanity_check, check_file_size
from ..arg_whitelist import ARGUMENT_WHITELIST

FIVE_GIGABYTES = 5 * 1024 * 1024 * 1024


class Tool:
    def __init__(self, tool_name, tool_version, tool_args, output_name,
                 output_path, inputs, min_inputs, max_inputs,
                 database_name=None, database_version=None,
                 input_prefix_mapping=None, parallel_enabled=False,
                 max_input_bytes_per_node=FIVE_GIGABYTES):
        self.tool_name = tool_name
        self.tool_version = tool_version
        self.tool_args = tool_args
        self.output_name = output_name
        self.output_path = output_path
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
        self.max_input_bytes_per_node = max_input_bytes_per_node
        self.query_threads = []
        self.query_thread_statuses = dict()

    def _validate_inputs(self):
        """Validates the input files. Currently only validates the number of inputs."""

        self.input_files = files_in_path(self.inputs)
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
        try:
            with open(self.output_path, "a") as _:
                pass
        except OSError:
            raise OSError("Output file path must be writable.")

        if not self.output_name:
            raise ValueError("output name must be non-empty.")

        # Perform a deeper input validation
        self._validate_inputs()

        # Perform a deeper tool_args validation
        self._validate_tool_args()

    def _validate_tool_args(self):
        """Validates and sanitizes user-provided custom tool_args.

        Currently, this is processed as an argument whitelist: argument tags
        are kept only if they appear as an accepted tag.
        """

        tool_dict = ARGUMENT_WHITELIST[self.tool_name]

        processed_args = []
        following_args = 0
        for arg in self.tool_args.split():
            if following_args == 0:
                if arg in tool_dict:
                    processed_args.append(arg)
                    following_args = tool_dict[arg]
            else:
                # TODO: filter out non-escaped bash command-line characters
                processed_args.append(arg)
                following_args -= 1

        sanitized_args = " ".join(processed_args)
        if sanitized_args != self.tool_args:
            self.tool_args = sanitized_args
            print("Processing tool_args as:")
            print(f"\t{self.tool_args}")

    def _merge_outputs(self, output_file_paths):
        raise NotImplementedError(f"Merging outputs not enabled for this tool {self.tool_name}")

    def _pretty_print_pipeline_segment_status(self, elapsed_seconds):
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

        print(f"\r{job_count} | {jobs_duration} {status_count}", end="\x1b[0K")

    def _wait_for_threads_to_finish(self):
        elapsed_seconds = 0
        for thread in self.query_threads:
            increment_seconds = 5
            while thread.is_alive():
                self._pretty_print_pipeline_segment_status(elapsed_seconds)
                elapsed_seconds += increment_seconds
                time.sleep(increment_seconds)
        print("")

        # Double check all threads are complete for safety
        for thread in self.query_threads:
            thread.join()

    def run(self):
        """Constructs and runs a Toolchest query."""
        # todo: better propagate and handle errors for parallel runs
        self._validate_args()

        print(f"Found {self.num_input_files} files to upload.")

        should_run_in_parallel = self.parallel_enabled \
            and self.num_input_files == 1 \
            and check_file_size(self.input_files[0]) > self.max_input_bytes_per_node

        adjusted_input_files = self.input_files
        if should_run_in_parallel:
            # Split single large input file into smaller acceptable files if parallelizing
            adjusted_input_files = split_file_by_lines(
                input_file_path=self.input_files[0],
                max_bytes=self.max_input_bytes_per_node,
            )
        else:
            # Make sure we're below plan/multi-part limit for non-splittable files
            for file_path in self.input_files:
                check_file_size(file_path, max_size_bytes=FIVE_GIGABYTES)

        # Set up the individual queries for parallelization
        # Note that this is relying on a result from the generator, so these are slightly staggered
        temp_input_file_paths = [] # this is not a generator, unlike adjusted_input_files
        temp_output_file_paths = []
        for index, input_file in enumerate(adjusted_input_files):
            temp_output_file_path = f"{self.output_path}_{index}"
            if should_run_in_parallel:
                temp_input_file_paths.append(input_file)
                temp_output_file_paths.append(temp_output_file_path)
            q = Query()

            # Deep copy to make thread safe
            query_args = copy.deepcopy({
                "tool_name": self.tool_name,
                "tool_version": self.tool_version,
                "tool_args": self.tool_args,
                "database_name": self.database_name,
                "database_version": self.database_version,
                "output_name": f"{index}_{self.output_name}",
                "input_files": [input_file],
                "input_prefix_mapping": self.input_prefix_mapping,
                "output_path": temp_output_file_path if should_run_in_parallel else self.output_path,
            })

            # Add non-distinct dictionary for status updates
            query_args["thread_statuses"] = self.query_thread_statuses

            new_thread = Thread(target=q.run_query, kwargs=query_args)
            self.query_threads.append(new_thread)

            print(f"Spawning job #{len(self.query_threads)}...")
            new_thread.start()
            time.sleep(15)

        print(f"Finished spawning jobs.")

        self._wait_for_threads_to_finish()

        print("Finished execution of parallel segments. Checking output...")

        # Do basic check for completion, merge output files, delete temporary files
        if should_run_in_parallel:
            for temp_output_file_path in temp_output_file_paths:
                sanity_check(temp_output_file_path)
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
            sanity_check(self.output_path)

        print("Analysis run complete!")


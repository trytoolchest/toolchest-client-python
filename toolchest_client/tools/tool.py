"""
toolchest_client.tools.tool
~~~~~~~~~~~~~~~~~~~~~~

This is the base class from which all tools descend.
Tool must be extended by an implementation (see kraken2.py) to be functional.
"""
from threading import Thread

from ..query import Query
from ..files import files_in_path, split_file_by_lines, sanity_check
from ..arg_whitelist import ARGUMENT_WHITELIST


class Tool:
    def __init__(self, tool_name, tool_version, tool_args, output_name,
                 output_path, inputs, min_inputs, max_inputs,
                 database_name=None, database_version=None,
                 input_prefix_mapping=None, parallel_enabled=False):
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

    def _validate_inputs(self):
        """Validates the input files. Currently only validates the number of inputs."""

        self.input_files = files_in_path(self.inputs)
        self.num_input_files = len(self.input_files)
        if  self.num_input_files < self.min_inputs:
            raise ValueError(f"Not enough input files submitted. "
                             f"Minimum is {self.min_inputs}, {self.num_input_files} found.")
        if  self.num_input_files > self.max_inputs:
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

    def run(self):
        """Constructs and runs a Toolchest query."""

        self._validate_args()

        # todo: check to see if we should even run in parallel
        if self.num_input_files == 1 and self.parallel_enabled:
            # Split single large input file into smaller acceptable files
            new_input_files = split_file_by_lines(
                input_file_path=self.input_files[0],
                max_bytes=30 * 1024 * 1024,  # todo: tool-by-tool max segment bytes for parallelization
            )

            # Set up the individual queries for parallelization
            query_threads = []
            temp_output_file_paths = []
            for index, input_file in enumerate(new_input_files):
                temp_output_file_path = f"{self.output_path}_{index}"  # todo: figure out what to do with the outputs
                temp_output_file_paths.append(temp_output_file_path)
                q = Query()
                query_threads.append(
                    Thread(target=q.run_query, kwargs={
                        "tool_name": self.tool_name,
                        "tool_version": self.tool_version,
                        "tool_args": self.tool_args,
                        "database_name": self.database_name,
                        "database_version": self.database_version,
                        "output_name": f"{index}_{self.output_name}",
                        "input_files": [input_file],
                        "input_prefix_mapping": self.input_prefix_mapping,
                        "output_path": temp_output_file_path,
                    })
                )

            print(f"Starting {len(query_threads)} new Toolchest instances...")

            # Invoke query for every segment of the file
            for thread in query_threads:
                thread.start()

            print(f"Finished starting Toolchest run."
                  f"Because this is a parallel run, progress will not be updated in real time."
                  f"Expect at most 30 minutes of runtime...")

            # Wait on completion
            for thread in query_threads:
                thread.join()

            print("Finished execution of parallel segments. Checking output...")

            # Do basic check for completion
            for temp_output_file_path in temp_output_file_paths:
                sanity_check(temp_output_file_path)

            # Merge files
            print(f"Merging {len(temp_output_file_paths)} output files...")
            self._merge_outputs(temp_output_file_paths)
            print(f"Merging of files complete")

        else:
            q = Query()
            q.run_query(
                tool_name=self.tool_name,
                tool_version=self.tool_version,
                tool_args=self.tool_args,
                database_name=self.database_name,
                database_version=self.database_version,
                output_name=self.output_name,
                input_files=self.input_files,
                input_prefix_mapping=self.input_prefix_mapping,
                output_path=self.output_path,
            )
    print("Analysis run complete!")

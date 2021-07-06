"""
toolchest_client.tools.tool
~~~~~~~~~~~~~~~~~~~~~~

This is the base class from which all tools descend.
Tool must be extended by an implementation (see kraken2.py) to be functional.
"""

from ..query import Query
from ..files import files_in_path


class Tool:
    def __init__(self, tool_name, tool_version, tool_args, output_name,
                 output_path, inputs, min_inputs, max_inputs,
                 database_name=None, database_version=None):
        self.tool_name = tool_name
        self.tool_version = tool_version
        self.tool_args = tool_args
        self.output_name = output_name
        self.output_path = output_path
        self.inputs = inputs
        self.input_files = None
        self.min_inputs = min_inputs
        self.max_inputs = max_inputs
        self.database_name = database_name
        self.database_version = database_version

    def _validate_inputs(self):
        """Validates the input files. Currently only validates the number of inputs."""

        self.input_files = files_in_path(self.inputs)
        num_input_files = len(self.input_files)
        if num_input_files < self.min_inputs:
            raise ValueError(f"Not enough input files submitted. "
                             f"Minimum is {self.min_inputs}, {num_input_files} found.")
        if num_input_files > self.min_inputs:
            raise ValueError(f"Too many input files submitted. "
                             f"Maximum is {self.max_inputs}, {num_input_files} found.")

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

    def run(self):
        """Constructs and runs a Toolchest query."""

        self._validate_args()

        q = Query()
        q.run_query(
            tool_name=self.tool_name,
            tool_version=self.tool_version,
            tool_args=self.tool_args,
            database_name=self.database_name,
            database_version=self.database_version,
            output_name=self.output_name,
            input_files=self.input_files,
            output_path=self.output_path,
        )

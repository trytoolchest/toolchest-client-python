"""
toolchest_client.tools.shogun
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This contains the shogun_align and shogun_filter implementations of the Tool class.
"""
from . import Tool
from toolchest_client.files import concatenate_files


class ShogunAlign(Tool):
    """
    The shogun_align implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path,
                 database_name, database_version):
        super().__init__(
            tool_name="shogun_align",
            tool_version="1.0.8",  # todo: allow shogun version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
            database_name=database_name,
            database_version=database_version,
            parallel_enabled=True,
        )

    def _merge_outputs(self, output_file_paths):
        concatenate_files(output_file_paths, self.output_path)


class ShogunFilter(Tool):
    """
    The shogun_filter implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path,
                 database_name, database_version):
        super().__init__(
            tool_name="shogun_filter",
            tool_version="1.0.8",  # todo: allow shogun version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
            database_name=database_name,
            database_version=database_version,
            parallel_enabled=True,
        )

    def _merge_outputs(self, output_file_paths):
        concatenate_files(output_file_paths, self.output_path)

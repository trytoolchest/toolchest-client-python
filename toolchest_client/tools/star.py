"""
toolchest_client.tools.STAR
~~~~~~~~~~~~~~~~~~~~~~

This is the STAR implementation of the Tool class.

Note: This tool is named STARInstance to differentiate it from
the STAR function called by the user, which is given in all caps
to be in line with the command-line argument.
"""
from . import Tool
from toolchest_client.files import merge_sam_files


class STARInstance(Tool):
    """
    The STAR implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, input_prefix_mapping,
                 output_path, database_name, database_version):
        super().__init__(
            tool_name="STAR",
            tool_version="2.7.9a",
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            input_prefix_mapping=input_prefix_mapping,
            min_inputs=1,
            max_inputs=2,
            database_name=database_name,
            database_version=database_version,
            parallel_enabled=True,
            max_input_bytes_per_node=4.5 * 1024 * 1024 * 1024,
        )

    def _merge_outputs(self, output_file_paths):
        merge_sam_files(output_file_paths, self.output_path)

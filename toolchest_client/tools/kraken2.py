"""
toolchest_client.tools.kraken2
~~~~~~~~~~~~~~~~~~~~~~

This is the Kraken2 implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import concatenate_files


class Kraken2(Tool):
    """
    The Kraken2 implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path,
                 database_name, database_version):
        super().__init__(
            tool_name="kraken2",
            tool_version="2.1.1",  # todo: allow kraken version to be set by the user
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

"""
toolchest_client.tools.BLASTN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the BLASTN implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType


class BLASTN(Tool):
    """
    The BLASTN implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path,
                 database_name, database_version, custom_database_path, **kwargs):
        super().__init__(
            tool_name="blastn",
            tool_version="2.13.0",
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            database_name=database_name,
            database_version=database_version,
            custom_database_path=custom_database_path,
            max_input_bytes_per_file=5 * 1024 * 1024 * 1024,
            output_type=OutputType.GZ_TAR,
            expected_output_file_names=["blastn_results.out"],
            **kwargs,
        )

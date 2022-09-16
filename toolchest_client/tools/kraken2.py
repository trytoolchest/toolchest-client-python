"""
toolchest_client.tools.kraken2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Kraken2 implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType
from toolchest_client.files.s3 import path_is_s3_uri


class Kraken2(Tool):
    """
    The Kraken2 implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path,
                 database_name, database_version, remote_database_path, tool_version='2.1.1', **kwargs):
        super().__init__(
            tool_name="kraken2",
            tool_version=tool_version,
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            database_name=database_name,
            database_version=database_version,
            remote_database_path=remote_database_path,
            max_input_bytes_per_file=64 * 1024 * 1024 * 1024,
            parallel_enabled=False,
            output_type=OutputType.S3 if path_is_s3_uri(output_path) else OutputType.GZ_TAR,
            expected_output_file_names=["kraken2_output.txt", "kraken2_report.txt"],
            **kwargs,
        )

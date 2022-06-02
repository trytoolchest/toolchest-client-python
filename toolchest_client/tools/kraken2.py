"""
toolchest_client.tools.kraken2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Kraken2 implementation of the Tool class.
"""
import os.path

from . import Tool
from toolchest_client.files import OutputType
from toolchest_client.files.s3 import path_is_s3_uri
from .tool_args import TOOL_ARG_LISTS


class Kraken2(Tool):
    """
    The Kraken2 implementation of the Tool class.
    """

    def __init__(self, tool_args, output_name, inputs, output_path,
                 database_name, database_version, custom_database_path, **kwargs):
        super().__init__(
            tool_name="kraken2",
            tool_version="2.1.1",  # todo: allow kraken 2 version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=2,
            database_name=database_name,
            database_version=database_version,
            custom_database_path=custom_database_path,
            max_input_bytes_per_file=64 * 1024 * 1024 * 1024,
            parallel_enabled=False,
            output_type=OutputType.S3 if path_is_s3_uri(output_path) else OutputType.GZ_TAR,
            output_is_directory=True,
            output_names=["kraken2_output.txt", "kraken2_report.txt"],
            **kwargs,
        )

"""
toolchest_client.tools.salmon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Salmon implementation of the Tool class.
"""
from toolchest_client.files import OutputType
from toolchest_client.files.s3 import path_is_s3_uri

from . import Tool


class Salmon(Tool):
    """
    The Salmon implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, database_name,
                 database_version, **kwargs):
        super().__init__(
            tool_name="salmon",
            tool_version="1.9.0",  # todo: allow salmon version to be set by the user
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            database_name=database_name,
            database_version=database_version,
            max_input_bytes_per_file=64 * 1024 * 1024 * 1024,
            output_type=OutputType.S3 if path_is_s3_uri(output_path) else OutputType.GZ_TAR,
            **kwargs,
        )

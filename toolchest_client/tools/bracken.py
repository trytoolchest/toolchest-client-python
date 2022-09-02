"""
toolchest_client.tools.bracken
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Bracken implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType
from toolchest_client.files.s3 import path_is_s3_uri


class Bracken(Tool):
    """
    The Bracken implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path,
                 database_name, database_version, remote_database_path, **kwargs):
        super().__init__(
            tool_name="bracken",
            tool_version="2.7",  # todo: allow bracken version to be set by the user
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            database_name=database_name,
            database_version=database_version,
            remote_database_path=remote_database_path,
            max_input_bytes_per_file=64 * 1024 * 1024 * 1024,
            output_type=OutputType.S3 if path_is_s3_uri(output_path) else OutputType.GZ_TAR,
            **kwargs,
        )

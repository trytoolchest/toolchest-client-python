"""
toolchest_client.tools.last
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Last implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType
from toolchest_client.files.s3 import path_is_s3_uri


class Lastal5(Tool):
    """
    The lastal5 implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, output_primary_name, database_name, database_version, **kwargs):
        super().__init__(
            tool_name="lastal5",
            tool_version="1411",
            tool_args=tool_args,
            output_path=output_path,
            output_primary_name=output_primary_name,
            inputs=inputs,
            database_name=database_name,
            database_version=database_version,
            max_input_bytes_per_file=64 * 1024 * 1024 * 1024,
            parallel_enabled=False,
            output_type=OutputType.S3 if path_is_s3_uri(output_path) else OutputType.GZ_TAR,
            **kwargs,
        )

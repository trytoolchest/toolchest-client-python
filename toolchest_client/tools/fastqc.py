"""
toolchest_client.tools.fastqc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the FastQC implementation of the Tool class.
"""
from toolchest_client.files import OutputType
from toolchest_client.files.s3 import path_is_s3_uri

from . import Tool


class FastQC(Tool):
    """
    The FastQC implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, **kwargs):
        super().__init__(
            tool_name="fastqc",
            tool_version="0.11.9",
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            max_input_bytes_per_file=64 * 1024 * 1024 * 1024,
            output_type=OutputType.S3 if path_is_s3_uri(output_path) else OutputType.GZ_TAR,
            **kwargs,
        )

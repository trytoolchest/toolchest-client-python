"""
toolchest_client.tools.transfer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the arbitrary file transfer implementation of the Tool class.
"""
from toolchest_client.files import OutputType, path_is_s3_uri

from . import Tool


class Transfer(Tool):
    """
    The arbitrary file transfer implementation of the Tool class.
    """
    def __init__(self, inputs, output_path, **kwargs):
        super().__init__(
            tool_name="transfer",
            tool_version="1.0.0",
            tool_args="",
            output_path=output_path,
            inputs=inputs,
            max_input_bytes_per_file=1024 * 1024 * 1024 * 1024,
            output_type=OutputType.S3 if path_is_s3_uri(output_path) else OutputType.GZ_TAR,
            expected_output_file_names=[],
            **kwargs,
        )

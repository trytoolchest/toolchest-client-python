"""
toolchest_client.tools.python3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Python3 implementation of the Tool class.
"""
from toolchest_client.files import OutputType, path_is_s3_uri

from . import Tool


class Python3(Tool):
    """
    The Python3 implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, **kwargs):
        super().__init__(
            tool_name="python3",
            tool_version="3.9.1",
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            output_type=OutputType.S3 if path_is_s3_uri(output_path) else OutputType.GZ_TAR,
            **kwargs,
        )

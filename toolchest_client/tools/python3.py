"""
toolchest_client.tools.test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the test implementation of the Tool class.
"""
import os
from toolchest_client.files import OutputType

from . import Tool


class Python3(Tool):
    """
    The Python3 implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path, **kwargs):
        super().__init__(
            tool_name="python3",
            tool_version="3.9.1",
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=100,
            parallel_enabled=False,
            output_type=OutputType.S3,
            output_is_directory=False,
            **kwargs,
        )

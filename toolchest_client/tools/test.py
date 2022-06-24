"""
toolchest_client.tools.test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the test implementation of the Tool class.
"""
from toolchest_client.files import OutputType

from . import Tool


class Test(Tool):
    """
    The test implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, **kwargs):
        super().__init__(
            tool_name="test",
            tool_version="0.1.0",
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            max_input_bytes_per_file=256 * 1024 * 1024 * 1024,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            expected_output_file_names=["test_output.txt"],
            **kwargs,
        )

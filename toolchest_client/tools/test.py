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
    def __init__(self, tool_args, output_name, inputs, output_path):
        super().__init__(
            tool_name="test",
            tool_version="0.1.0",
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=100,  # this limit is completely arbitrary
            max_input_bytes_per_file=256 * 1024 * 1024 * 1024,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            output_is_directory=True,
            output_names=["test_output.txt"],
        )

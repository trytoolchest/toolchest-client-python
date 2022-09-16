"""
toolchest_client.tools.demucs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Demucs implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType


class Demucs(Tool):
    """
    The Demucs implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, **kwargs):
        super().__init__(
            tool_name="demucs",
            tool_version='3.0.4',
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            expected_output_file_names=["error.log", "output.log"],
            **kwargs,
        )

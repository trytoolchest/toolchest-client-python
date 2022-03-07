"""
toolchest_client.tools.demucs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Demucs implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType


class Demucs(Tool):
    """
    The Demucs Omega implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path, **kwargs):
        super().__init__(
            tool_name="demucs",
            tool_version='3.0.4',
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            output_is_directory=True,
            output_names=["error.log", "output.log"],
            **kwargs,
        )

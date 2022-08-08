"""
toolchest_client.tools.humann
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the HUMAnN implementation of the Tool class.
"""
from toolchest_client.files import OutputType

from . import Tool


class HUMAnN(Tool):
    """
    The HUMAnN implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, **kwargs):
        super().__init__(
            tool_name="humann",
            tool_version="3.1.1",  # todo: allow version to be set by the user
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            **kwargs,
        )

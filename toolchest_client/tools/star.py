"""
toolchest_client.tools.star
~~~~~~~~~~~~~~~~~~~~~~

This is the STAR implementation of the Tool class.
"""
from . import Tool


class STAR(Tool):
    """
    The STAR implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path):
        super().__init__(
            tool_name="star",
            tool_version="2.7.9",
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=2,
            max_inputs=2,
        )

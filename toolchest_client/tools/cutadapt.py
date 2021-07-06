"""
toolchest_client.tools.cutadapt
~~~~~~~~~~~~~~~~~~~~~~

This is the cutadapt implementation of the Tool class.
"""
from . import Tool


class Cutadapt(Tool):
    """
    The cutadapt implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path):
        super().__init__(
            tool_name="cutadapt",
            tool_version="3.4",  # todo: allow cutadapt version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
        )

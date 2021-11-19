"""
toolchest_client.tools.megahit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the megahit implementation of the Tool class.
"""
from . import Tool


class Megahit(Tool):
    """
    The megahit implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, input_prefix_mapping,
                 output_path):
        super().__init__(
            tool_name="megahit",
            tool_version="1.2.9",  # todo: allow version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            input_prefix_mapping=input_prefix_mapping,
            min_inputs=1,
            max_inputs=10,  # todo: make this unlimited?
        )
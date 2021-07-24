"""
toolchest_client.tools.unicycler
~~~~~~~~~~~~~~~~~~~~~~

This is the Unicycler implementation of the Tool class.
"""
from . import Tool


class Unicycler(Tool):
    """
    The unicycler implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, input_prefix_mapping,
                 output_path):
        super().__init__(
            tool_name="unicycler",
            tool_version="0.4.9",  # todo: allow unicycler version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            input_prefix_mapping=input_prefix_mapping,
            min_inputs=1,
            max_inputs=3,
        )

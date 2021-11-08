"""
toolchest_client.tools.shi7
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the shi7 implementation of the Tool class.
"""
from . import Tool


class Shi7(Tool):
    """
    The shi7 implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path):
        super().__init__(
            tool_name="shi7",
            tool_version="1.0.3",  # todo: allow shi7 version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=10,  # artificially constrained at 10 for now
            parallel_enabled=False,
        )

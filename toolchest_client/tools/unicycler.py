"""
toolchest_client.tools.unicycler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Unicycler implementation of the Tool class.
"""
from toolchest_client.files import OutputType

from . import Tool


class Unicycler(Tool):
    """
    The unicycler implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, input_prefix_mapping,
                 output_path, **kwargs):
        super().__init__(
            tool_name="unicycler",
            tool_version="0.4.9",  # todo: allow unicycler version to be set by the user
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            input_prefix_mapping=input_prefix_mapping,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            expected_output_file_names=["assembly.fasta", "unicycler.log"],
            **kwargs,
        )

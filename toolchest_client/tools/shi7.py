"""
toolchest_client.tools.shi7
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the shi7 implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType


class Shi7(Tool):
    """
    The shi7 implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path, **kwargs):
        super().__init__(
            tool_name="shi7",
            tool_version="1.0.3",  # todo: allow shi7 version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=None,  # note: no limit is set on the # of inputs
            parallel_enabled=False,
            group_paired_ends=True,
            max_input_bytes_per_file=16 * 1024 * 1024 * 1024,
            output_type=OutputType.GZ_TAR,
            output_is_directory=True,
            output_names=["combined_seqs.fna", "shi7.log"],
            **kwargs,
        )

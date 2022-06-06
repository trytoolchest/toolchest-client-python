"""
toolchest_client.tools.AlphaFold
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the AlphaFold implementation of the Tool class.
"""
from toolchest_client.files import OutputType
from . import Tool


class AlphaFold(Tool):
    """
    The AlphaFold implementation of the Tool class.
    """
    def __init__(self, inputs, output_path, tool_args, **kwargs):
        super().__init__(
            tool_name="alphafold",
            tool_version="2.1.2",
            tool_args=tool_args,
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
            database_name="alphafold_standard",
            database_version="2.1.2",
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            output_path=output_path,
            output_is_directory=True,
            **kwargs,
        )

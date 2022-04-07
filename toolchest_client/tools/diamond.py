"""
toolchest_client.tools.Diamond
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Diamond implementation of the Tool class.
"""
import os

from toolchest_client.files import OutputType
from . import Tool


class DiamondBlastp(Tool):
    """
    The Diamond Blastp implementation of the Tool class.
    """
    def __init__(self, inputs, output_name, output_path, tool_args, **kwargs):
        super().__init__(
            tool_name="diamond_blastp",
            tool_version="2.0.14",
            tool_args=tool_args,
            output_name=output_name,
            output_primary_name=os.path.basename(output_path),
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
            database_name="diamond_blastp_standard",
            database_version="1",
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            output_path=output_path,
            output_is_directory=False,
            **kwargs,
        )
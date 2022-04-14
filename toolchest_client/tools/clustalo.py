"""
toolchest_client.tools.clustalo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Clustal Omega implementation of the Tool class.
"""
import os

from . import Tool
from toolchest_client.files import OutputType


class ClustalO(Tool):
    """
    The Clustal Omega implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path, **kwargs):
        output_primary_name = os.path.basename(output_path)
        super().__init__(
            tool_name="clustalo",
            tool_version='1.2.4',
            tool_args=tool_args,
            output_name=output_name,
            output_primary_name=output_primary_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            output_is_directory=False,
            output_names=[output_primary_name, f"{output_primary_name}.log"],
            **kwargs,
        )

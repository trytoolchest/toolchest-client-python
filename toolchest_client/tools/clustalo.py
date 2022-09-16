"""
toolchest_client.tools.clustalo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Clustal Omega implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType


class ClustalO(Tool):
    """
    The Clustal Omega implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, output_primary_name, **kwargs):
        super().__init__(
            tool_name="clustalo",
            tool_version='1.2.4',
            tool_args=tool_args,
            output_primary_name=output_primary_name,
            output_path=output_path,
            inputs=inputs,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            expected_output_file_names=[output_primary_name, f"{output_primary_name}.log"],
            **kwargs,
        )

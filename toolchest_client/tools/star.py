"""
toolchest_client.tools.STAR
~~~~~~~~~~~~~~~~~~~~~~

This is the STAR implementation of the Tool class.
"""
from . import Tool


class STAR(Tool):
    """
    The STAR implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path,
                 database_name, database_version):
        super().__init__(
            tool_name="STAR",
            tool_version="2.7.9a",
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=2,
            database_name=database_name,
            database_version=database_version,
        )

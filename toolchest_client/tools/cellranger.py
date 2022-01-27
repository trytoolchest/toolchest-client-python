"""
toolchest_client.tools.cellranger
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This contains the cellranger_mkfastq implementations of the Tool class.
"""
from . import Tool


class CellRangerMkfastq(Tool):
    """
    The cellranger_mkfastq implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path):
        super().__init__(
            tool_name="cellranger_mkfastq",
            tool_version="6.1.1",  # todo: allow cellranger version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
            compress_inputs=True,
        )


class CellRangerCount(Tool):
    """
    The cellranger_count implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path,
                 database_name, database_version):
        super().__init__(
            tool_name="cellranger_count",
            tool_version="6.1.1",  # todo: allow cellranger version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
            database_name=database_name,
            database_version=database_version,
            compress_inputs=True,
        )

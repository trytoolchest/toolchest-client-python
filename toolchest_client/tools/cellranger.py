"""
toolchest_client.tools.cellranger
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This contains the cellranger implementations of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType


class CellRangerCount(Tool):
    """
    The cellranger_count implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, database_name,
                 database_version, **kwargs):
        super().__init__(
            tool_name="cellranger_count",
            tool_version="6.1.2",  # todo: allow cellranger version to be set by the user
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
            database_name=database_name,
            database_version=database_version,
            compress_inputs=True,
            max_input_bytes_per_file=128 * 1024 * 1024 * 1024,
            output_type=OutputType.GZ_TAR,
            **kwargs,
        )

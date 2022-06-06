"""
toolchest_client.tools.rapsearch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Rapsearch implementation of the Tool class.
"""
import os

from . import Tool
from toolchest_client.files import OutputType


class Rapsearch2(Tool):
    """
    The Rapsearch implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, database_name,
                 database_version, **kwargs):
        output_primary_name = os.path.basename(output_path)
        super().__init__(
            tool_name="rapsearch2",
            tool_version="2.24",
            tool_args=tool_args,
            output_primary_name=output_primary_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
            database_name=database_name,
            database_version=database_version,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            output_is_directory=False,
            expected_output_file_names=[f"{output_primary_name}.m8"],  # .aln output may be omitted with certain args
            **kwargs,
        )

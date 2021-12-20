"""
toolchest_client.tools.kraken2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Kraken2 implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType


class Kraken2(Tool):
    """
    The Kraken2 implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path,
                 database_name, database_version):
        super().__init__(
            tool_name="kraken2",
            tool_version="2.1.1",  # todo: allow kraken 2 version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=2,
            database_name=database_name,
            database_version=database_version,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            output_is_directory=True,
            output_names=["kraken2_output.txt", "kraken2_report.txt"]
        )

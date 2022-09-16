"""
toolchest_client.tools.bowtie2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the bowtie2 implementation of the Tool class.
"""
from toolchest_client.files import OutputType

from . import Tool


class Bowtie2(Tool):
    """
    The bowtie2 implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, database_name,
                 database_version, **kwargs):
        super().__init__(
            tool_name="bowtie2",
            tool_version="2.4.4",  # todo: allow bowtie2 version to be set by the user
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            database_name=database_name,
            database_version=database_version,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            expected_output_file_names=["bowtie2.log", "bowtie2_output.sam"],
            **kwargs,
        )

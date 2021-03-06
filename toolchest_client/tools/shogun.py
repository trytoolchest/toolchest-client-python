"""
toolchest_client.tools.shogun
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This contains the shogun_align and shogun_filter implementations of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType


class ShogunAlign(Tool):
    """
    The shogun_align implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, database_name,
                 database_version, **kwargs):
        super().__init__(
            tool_name="shogun_align",
            tool_version="1.0.8",  # todo: allow shogun version to be set by the user
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            database_name=database_name,
            database_version=database_version,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            expected_output_file_names=["alignment.bowtie2.sam"],
            **kwargs,
        )


class ShogunFilter(Tool):
    """
    The shogun_filter implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, database_name,
                 database_version, **kwargs):
        super().__init__(
            tool_name="shogun_filter",
            tool_version="1.0.8",  # todo: allow shogun version to be set by the user
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,
            database_name=database_name,
            database_version=database_version,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            expected_output_file_names=["combined_seqs.filtered.fna", "alignment.burst.best.b6"],
            **kwargs,
        )

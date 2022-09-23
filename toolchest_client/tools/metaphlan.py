"""
toolchest_client.tools.metaphlan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the MetaPhlAn implementation of the Tool class.
"""
from toolchest_client.files import OutputType
from toolchest_client.files.s3 import path_is_s3_uri

from . import Tool


class MetaPhlAn(Tool):
    """
    The MetaPhlAn implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, output_primary_name, **kwargs):
        super().__init__(
            tool_name="metaphlan",
            tool_version="3.0.14",
            tool_args=tool_args,
            output_path=output_path,
            database_name="metaphlan_mpa_v30_CHOCOPhlAn_201901",
            database_version="1",
            output_primary_name=output_primary_name,
            inputs=inputs,
            max_inputs=1,
            max_input_bytes_per_file=64 * 1024 * 1024 * 1024,
            output_type=OutputType.S3 if path_is_s3_uri(output_path) else OutputType.GZ_TAR,
            **kwargs,
        )

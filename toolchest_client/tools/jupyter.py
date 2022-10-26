"""
toolchest_client.tools.jupyter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Jupyter implementation of the Tool class.
"""
from toolchest_client.files import OutputType, path_is_s3_uri

from . import Tool


class Jupyter(Tool):
    """
    The Jupyter implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, input_prefix_mapping, **kwargs):
        super().__init__(
            tool_name="jupyter",
            tool_version="1",
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            input_prefix_mapping=input_prefix_mapping,
            output_primary_name="token.txt",
            output_type=OutputType.S3 if path_is_s3_uri(output_path) else OutputType.FLAT_TEXT,
            **kwargs,
        )

"""
toolchest_client.tools.lug
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Lug implementation of the Tool class.
"""
from toolchest_client.files import OutputType, path_is_s3_uri

from . import Tool


class Lug(Tool):
    """
    The Lug implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_path, tool_version,
                 custom_docker_image_id=None, universal_name=None, **kwargs):
        super().__init__(
            tool_name="lug",
            tool_version=tool_version,
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            max_input_bytes_per_file=4 * 1024 * 1024 * 1024 * 1024,
            output_type=OutputType.S3 if path_is_s3_uri(output_path) else OutputType.GZ_TAR,
            custom_docker_image_id=custom_docker_image_id,
            universal_name=universal_name,
            **kwargs,
        )

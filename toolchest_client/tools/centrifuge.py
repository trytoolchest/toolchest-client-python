"""
toolchest_client.tools.centrifuge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the centrifuge implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType, sanity_check


class Centrifuge(Tool):
    """
    The centrifuge implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, input_prefix_mapping,
                 output_path, **kwargs):
        super().__init__(
            tool_name="centrifuge",
            tool_version="1.0.4",  # todo: allow version to be set by the user
            tool_args=tool_args,
            output_path=output_path,
            inputs=inputs,
            input_prefix_mapping=input_prefix_mapping,
            max_inputs=None,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            expected_output_file_names=[
                "centrifuge_output.txt",
                "centrifuge_report.tsv",
            ],
            **kwargs,
        )

    def _postflight(self, output):
        if self.output_validation_enabled:
            for output_file_name in self.expected_output_file_names:
                # Skip validation for the "done" file, which should be empty.
                if output_file_name != "done":
                    output_file_path = f"{self.output_path}/{output_file_name}"
                    sanity_check(output_file_path)

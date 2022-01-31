"""
toolchest_client.tools.megahit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the megahit implementation of the Tool class.
"""
from . import Tool
from toolchest_client.files import OutputType, sanity_check


class Megahit(Tool):
    """
    The megahit implementation of the Tool class.
    """

    def __init__(
        self, tool_args, output_name, inputs, input_prefix_mapping, output_path
    ):
        super().__init__(
            tool_name="megahit",
            tool_version="1.2.9",  # todo: allow version to be set by the user
            tool_args=tool_args,
            output_name=output_name,
            output_path=output_path,
            inputs=inputs,
            input_prefix_mapping=input_prefix_mapping,
            min_inputs=1,
            max_inputs=None,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            output_is_directory=True,
            output_names=[
                "checkpoints.txt",
                "done",
                "final.contigs.fa",
                "log",
                "options.json",
            ],
        )

    def _postflight(self):
        if self.output_validation_enabled:
            for output_name in self.output_names:
                # Skip validation for the "done" file, which should be empty.
                if output_name != "done":
                    output_file_path = f"{self.output_path}/{output_name}"
                    sanity_check(output_file_path)

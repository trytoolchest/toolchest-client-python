"""
toolchest_client.tools.kraken2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Kraken2 implementation of the Tool class.
"""
import os

from . import Tool
from toolchest_client.files import OutputType, assert_exists


class Kraken2(Tool):
    """
    The Kraken2 implementation of the Tool class.
    """
    def __init__(self, tool_args, output_name, inputs, output_path,
                 database_name, database_version):
        super().__init__(
            tool_name="kraken2",
            tool_version="2.1.1",  # todo: allow kraken version to be set by the user
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
        )

    def _preflight(self):
        """Kraken 2 specific preflight"""
        super()._preflight()

        if os.path.exists(self.output_path):
            if os.path.isfile(self.output_path):
                raise ValueError(
                    f"{self.output_path} is a file. Please pass a directory instead of an output file."
                )
        else:
            os.makedirs(self.output_path)

        for file_path in ["kraken2_output.txt", "kraken2_report.txt", "output", "output.tar.gz"]:
            joined_file_path = os.path.join(self.output_path, file_path)
            if os.path.exists(joined_file_path):
                print(f"WARNING: {joined_file_path} already exists and will be overwritten")

    def _postflight(self):
        """Kraken 2 specific postflight"""
        # Do a basic sanity check on the output files
        for output_name in ["kraken2_output.txt", "kraken2_report.txt"]:
            output_file_path = f"{self.output_path}/{output_name}"
            assert_exists(output_file_path, must_be_file=True)
            if os.stat(output_file_path).st_size <= 100:
                raise ValueError(f"Kraken 2 output file at {output_file_path} is suspiciously small")

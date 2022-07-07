"""
toolchest_client.api.output
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides an Output object returned by any completed queries
made by Toolchest tools. The output object contains information about
where the output file can be located.

Note: The Output object does NOT represent the contents of any of the
tool output files themselves.
"""

from toolchest_client.api.download import download
from toolchest_client.api.status import get_status


class Output:
    """A Toolchest query output.

    Provides information about location of output file(s), both locally
    (if downloaded) and in the cloud.

    """

    def __init__(self, s3_uri=None, output_path=None, run_id=None):
        self.tool_name = None
        self.tool_version = None
        self.database_name = None
        self.database_version = None
        self.s3_uri = s3_uri
        self.output_path = output_path
        self.output_file_paths = None
        self.run_id = run_id

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def set_run_id(self, run_id):
        self.run_id = run_id

    def set_s3_uri(self, s3_uri):
        self.s3_uri = s3_uri

    def set_output_path(self, output_path, output_file_paths=None):
        self.output_path = output_path
        self.output_file_paths = output_file_paths

    def set_tool(self, tool_name=None, tool_version=None):
        """Sets the tool name and tool version for ensuring versioning and reproducibility."""
        self.tool_name = tool_name
        self.tool_version = tool_version

    def set_database(self, database_name=None, database_version=None):
        """Sets the database name and database version for ensuring versioning and reproducibility.

        `database_version` increments when updating a database through the API.
        """
        self.database_name = database_name
        self.database_version = database_version

    def download(self, output_path=None, output_dir=None, skip_decompression=False):
        if not output_path:
            if not output_dir:
                raise ValueError("Output destination directory (output_path) must be specified.")
            output_path = output_dir  # backwards compatibility for old calls

        self.output_file_paths = download(
            output_path=output_path,
            s3_uri=self.s3_uri,
            run_id=self.run_id,
            skip_decompression=skip_decompression,
        )
        return self.output_file_paths

    def get_status(self):
        """
        Returns the status of a run. Only for use when the Output instance is initialized with a run_id.
        """
        if not self.run_id:
            raise ValueError("Cannot get status on an output that has no run_id")
        return get_status(self.run_id)

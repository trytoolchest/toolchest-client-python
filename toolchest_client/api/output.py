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
        self.s3_uri = s3_uri
        self.output_path = output_path
        self.run_id = run_id,

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def set_run_id(self, run_id):
        self.run_id = run_id

    def set_s3_uri(self, s3_uri):
        self.s3_uri = s3_uri

    def set_output_path(self, output_path):
        self.output_path = output_path

    def download(self, output_dir, skip_decompression=False):
        self.output_path = download(
            output_path=output_dir,
            s3_uri=self.s3_uri,
            run_id=self.run_id,
            skip_decompression=skip_decompression,
        )
        return self.output_path

    def get_status(self):
        """
        Returns the status of a run. Only for use when the Output instance is initialized with a run_id.
        """
        if not self.run_id:
            raise ValueError("Cannot get status on an output that has no run_id")
        return get_status(self.run_id)

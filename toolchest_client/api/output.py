"""
toolchest_client.api.output
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides an Output object returned by any completed queries
made by Toolchest tools. The output object contains information about
where the output file can be located.

Note: The Output object does NOT represent any of the tool outputs
themselves.
"""


class Output:
    """A Toolchest query output.

    Provides information about location of output file(s), both locally
    (if downloaded) and in the cloud.

    """

    def __init__(self, s3_uri=None, presigned_s3_url=None, output_path=None):
        self.s3_uri = s3_uri
        self.presigned_s3_url = presigned_s3_url
        self.output_path = output_path

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)
"""
toolchest_client.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains custom exceptions used for the Toolchest client.
"""


class ToolchestException(OSError):
    """There was an unknown exception that occurred during your
    Toolchest job.
    """


class ToolchestKeyError(ToolchestException):
    """Invalid Toolchest auth key."""


class DataLimitError(ToolchestException):
    """Data limit for Toolchest exceeded."""


class ToolchestJobError(ToolchestException):
    """An error occurred when running the job instance."""

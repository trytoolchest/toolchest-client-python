"""
toolchest_client.api.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains custom exceptions used for the Toolchest client.
"""


class ToolchestException(OSError):
    """There was an unknown exception that occurred during your
    Toolchest job.
    """


class ToolchestKeyError(ToolchestException):
    """Invalid Toolchest auth key."""

class ToolchestS3AccessError(ToolchestException):
    """S3 input cannot be accessed by Toolchest."""

class DataLimitError(ToolchestException):
    """Data limit for Toolchest exceeded."""


class ToolchestJobError(ToolchestException):
    """An error occurred when running the job instance."""

"""
toolchest_client.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains custom exceptions used for the Toolchest client.
"""

class ToolchestException(OSError):
    """There was an unknown exception that occurred during your
    Toolchest job.
    """

class DataLimitError(ToolchestException):
    """Data limit for Toolchest exceeded."""

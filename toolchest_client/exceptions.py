"""
toolchest_client.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains custom exceptions used for the Toolchest client.
"""

class ToolchestException(IOError):
    """There was an ambiguous exception that occured during your
    Toolchest job.
    """

    def __init__(self):
        pass

class DataLimitError(ToolchestException):
    """Data limit for Toolchest exceeded."""

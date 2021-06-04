"""
toolchest_client._internal_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides internal utility functions for running Toolchest tools.
"""


def _validate_tool_kwargs(**kwargs):
    """Validates kwargs passed to (specific) tool functions."""

    # Default values for query parameters input_name and output_name are provided
    # by default in tool function; they should not be provided by the user.
    if "input_name" in kwargs:
        raise ValueError("input_name should not be manually specified")
    if "output_name" in kwargs:
        raise ValueError("output_name should not be manually specified")

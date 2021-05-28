"""
toolchest_client.status
~~~~~~~~~~~~~~~~~~~~~~~

This module contains a Status class for status updates to the Toolchest API.
"""

from enum import Enum

class Status(Enum):
    """Status values for the Toolchest API."""

    INITIALIZED = "initialized"
    TRANSFERRING_FROM_CLIENT = "transferring_from_client"
    TRANSFERRED_FROM_CLIENT = "transferred_from_client"
    AWAITING_EXECUTION = "awaiting_execution"
    BEGINNING_EXECUTION = "beginning_execution"
    EXECUTING = "executing"
    READY_TO_TRANSFER_TO_CLIENT = "ready_to_transfer_to_client"
    TRANSFERRING_TO_CLIENT = "transferring_to_client"
    TRANSFERRED_TO_CLIENT = "transferred_to_client"

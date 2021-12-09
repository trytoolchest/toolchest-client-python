"""
toolchest_client.api.status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains a Status class for status updates to the Toolchest API.
"""

from enum import Enum


class Status(str, Enum):
    """Status values for the Toolchest API."""

    # NOTE: These statuses aren't currently being used with threading.
    # All status updates are encapsulated in the statuses of the threads.
    INITIALIZED = "initialized"
    TRANSFERRING_FROM_CLIENT = "transferring_from_client"
    TRANSFERRED_FROM_CLIENT = "transferred_from_client"
    AWAITING_EXECUTION = "awaiting_execution"
    BEGINNING_EXECUTION = "beginning_execution"
    EXECUTING = "executing"
    READY_TO_TRANSFER_TO_CLIENT = "ready_to_transfer_to_client"
    TRANSFERRING_TO_CLIENT = "transferring_to_client"
    TRANSFERRED_TO_CLIENT = "transferred_to_client"
    COMPLETE = "complete"
    FAILED = "failed"


class ThreadStatus(str, Enum):
    """Status values for local threads"""

    INITIALIZED = "initialized"
    UPLOADING = "uploading"
    EXECUTING = "executing"
    DOWNLOADING = "downloading"
    COMPLETE = "complete"
    INTERRUPTING = "interrupting"
    FAILED = "failed"

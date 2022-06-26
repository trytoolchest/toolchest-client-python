"""
toolchest_client.api.status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains a function to check pipeline_segment_instance statuses and status enums.
"""

from enum import Enum


def get_status(run_id):
    """Returns the status of the Toolchest run.

        Call this less than once a second to avoid being rate-limited.

        :param run_id: the ID returned by a tool. Internally, this ID is the pipeline_segment_instance_id.
        """
    from toolchest_client.api.query import Query  # local import to avoid circular dependency

    query = Query(
        is_async=True,
        pipeline_segment_instance_id=run_id,
    )

    return query.get_job_status()


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

    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    UPLOADING = "uploading"
    EXECUTING = "executing"
    DOWNLOADING = "downloading"
    COMPLETE = "complete"
    INTERRUPTING = "interrupting"
    FAILED = "failed"

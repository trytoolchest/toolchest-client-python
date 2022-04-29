"""
toolchest_client.api.urls
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module serves as a single source for URLs used in
Toolchest queries and API calls.
"""

import os

# Base URLs used by the server API.
API_URL = os.environ.get("API_URL", "https://api.toolche.st")

PIPELINE_SEGMENT_INSTANCES_ROUTE = "/pipeline-segment-instances"
PIPELINE_SEGMENT_INSTANCES_URL = API_URL + PIPELINE_SEGMENT_INSTANCES_ROUTE

S3_ROUTE = "/s3"
S3_URL = API_URL + S3_ROUTE
S3_METADATA_URL = S3_URL + "/metadata"

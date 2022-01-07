"""
toolchest_client.api.urls
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module serves as a single source for URLs used in
Toolchest queries and API calls.
"""

import os

# Base URLs used by the server API.
BASE_URL = os.environ.get("BASE_URL", "https://api.toolche.st")
PIPELINE_ROUTE = "/pipeline-segment-instances"
PIPELINE_URL = BASE_URL + PIPELINE_ROUTE


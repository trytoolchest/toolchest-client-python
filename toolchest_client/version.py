"""
toolchest_client.version
~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the version for each tool (required by the server API).
"""

from enum import Enum

class Version(Enum):
    """Versions of Toolchest tools, to be passed to the query."""

    CUTADAPT = "1.0"
    KRAKEN2 = "2.1.1"

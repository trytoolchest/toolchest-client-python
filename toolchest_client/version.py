"""
toolchest_client.version
~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the latest version for each tool, needed for the query.
"""

from enum import Enum

class Version(Enum):
    """Versions of Toolchest tools, to be passed to the query."""

    CUTADAPT = "1.0"
    KRAKEN2 = "2.1.1"

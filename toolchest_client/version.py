"""
toolchest_client.version
~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the version for each tool (required by the server API).
"""

from enum import Enum

class Version(Enum):
    """Versions of Toolchest tools, to be passed to the query."""

    BOWTIE2 = "2.4.4"
    CUTADAPT = "3.4"
    KRAKEN2 = "2.1.1"
    TEST = "0.1.0"

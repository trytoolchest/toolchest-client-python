# TODO: include a docstring here

import builtins
from dotenv import load_dotenv, find_dotenv
import functools

# set __version__ module
try:
    # importlib.metadata is present in Python 3.8 and later
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata as importlib_metadata
__version__ = importlib_metadata.version(__package__ or __name__)

# .env load must be before imports that use environment variables
load_dotenv(find_dotenv(".env"))

# specifying print flushing is necessary to support loading from R
builtins.print = functools.partial(print, flush=True)

from toolchest_client.api.auth import get_key, set_key
from toolchest_client.api.exceptions import ToolchestException, DataLimitError, ToolchestJobError
from toolchest_client.api.query import Query
from .tools.api import bowtie2, cellranger_mkfastq, kraken2, shi7, shogun_align, shogun_filter, STAR, test, unicycler

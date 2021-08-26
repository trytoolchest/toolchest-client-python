# TODO: include a docstring here

import builtins
from dotenv import load_dotenv, find_dotenv
import functools

# .env load must be before imports that use environment variables
load_dotenv(find_dotenv(".env"))

# specifying print flushing is necessary to support loading from R
builtins.print = functools.partial(print, flush=True)

from toolchest_client.api.auth import get_key, set_key
from toolchest_client.api.exceptions import ToolchestException, DataLimitError, ToolchestJobError
from toolchest_client.api.query import Query
from .tools.api import bowtie2, cutadapt, kraken2, STAR, test, unicycler

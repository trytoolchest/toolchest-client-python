# TODO: include a docstring here

import builtins
from dotenv import load_dotenv, find_dotenv
import functools

# .env load must be before imports that use environment variables
load_dotenv(find_dotenv(".env"))

# specifying print flushing is necessary to support loading from R
builtins.print = functools.partial(print, flush=True)

from .auth import get_key, set_key
from .exceptions import ToolchestException, DataLimitError
from .query import Query
from .tools.api import bowtie2, cutadapt, kraken2, test, unicycler

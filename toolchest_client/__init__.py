import builtins
from dotenv import load_dotenv, find_dotenv
import functools

from .logging import setup_logging

# set __version__ module
try:
    # importlib.metadata is present in Python 3.8 and later
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata as importlib_metadata
try:
    __version__ = importlib_metadata.version(__package__ or __name__)
except importlib_metadata.PackageNotFoundError:
    __version__ = None

# .env load must be before imports that use environment variables
load_dotenv(find_dotenv(".env"))

# specifying print flushing is necessary to support loading from R
builtins.print = functools.partial(print, flush=True)

# configure logger
setup_logging()

from toolchest_client.api.auth import get_key, set_key
from toolchest_client.api.download import download
from toolchest_client.api.exceptions import ToolchestException, DataLimitError, ToolchestJobError, \
    ToolchestDownloadError
from toolchest_client.api.query import Query
from toolchest_client.api.status import Status, get_status
from toolchest_client.api.urls import get_api_url, set_api_url
from .tools.api import add_database, alphafold, blastn, bowtie2, bracken, cellranger_count, centrifuge, clustalo, \
    demucs, diamond_blastp, diamond_blastx, fastqc, humann3, jupyter, kallisto, kraken2, lastal5, lug, megahit, \
    metaphlan, python3, rapsearch, rapsearch2, salmon, shi7, shogun_align, shogun_filter, STAR, test, transfer, \
    unicycler, update_database

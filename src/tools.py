from .query import Query
from .version import Version

def query(tool, version, **kwargs):
    """
    TODO: Document
    """

    with Query() as q:
        q.run_query(tool, version, **kwargs)

def cutadapt(cutadapt_args, **kwargs):
    query_kwargs = dict(tool_args=cutadapt_args, kwargs)
    query("cutadapt", Version.CUTADAPT.value, **query_kwargs))

def kraken2(kraken2_args="", **kwargs):
    query_kwargs = dict(tool_args=cutadapt_args, kwargs)
    query("kraken2", Version.KRAKEN2.value, **query_kwargs)

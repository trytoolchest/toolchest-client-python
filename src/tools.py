from .query import Query
from .version import Version

def run_tool(tool, version, **kwargs):
    """
    TODO: Document
    """

    q = Query()
    q.run_query(tool, version, **kwargs)

def cutadapt(cutadapt_args, **kwargs):
    run_tool(
        "cutadapt",
        Version.CUTADAPT.value,
        tool_args=cutadapt_args,
        input_name="input.fastq",
        output_name="output.fastq",
        **kwargs
    )

def kraken2(kraken2_args="", **kwargs):
    run_tool(
        "kraken2",
        Version.KRAKEN2.value,
        tool_args=kraken2_args,
        input_name="input.fastq",
        output_name="output.txt",
        **kwargs
    )

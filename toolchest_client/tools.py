"""
toolchest_client.tools
~~~~~~~~~~~~~~~~~~~~~~

This module contains the API for using Toolchest tools.
"""

from ._internal_utils import _validate_tool_kwargs
from .query import Query
from .version import Version

def run_tool(tool, version, **kwargs):
    """Constructs and runs a Toolchest query.

    :param tool: Tool to be used.
    :param version: Version of tool to be used.
    :param tool_args: Tool-specific arguments to be passed to the tool.
    :param input_name: Internal name of file inputted to the tool.
    :param output_name: Internal name of file outputted by the tool.
    :param input_path: Path (client-side) of file to be passed in as input.
    :param output_path: Path (client-side) where the output file will be downloaded.
    """

    q = Query()
    q.run_query(tool, version, **kwargs)

def cutadapt(cutadapt_args, **kwargs):
    """Runs Cutadapt via Toolchest.

    (Currently, only single .fastq inputs are supported.)

    :param cutadapt_args: Additional arguments to be passed to Cutadapt.
    :param input_path: Path (client-side) of file to be passed in as input.
    :param output_path: Path (client-side) where the output file will be downloaded.

    .. note:: Do **NOT** include the output path (`-o output_path`) or the
      input path (`input_path` at the end) in the passed `cutadapt_args`. Inputs
      and outputs will be automatically handled by the Toolchest backend, and
      including these arguments will lead to errors or undesired output.

    Usage::

        >>> import toolchest_client as tc
        >>> tc.cutadapt(
        ...     "-a AACCGGTT",
        ...     input_path="./path/to/input",
        ...     output_path="./path/to/output",
        ... )

    """

    _validate_tool_kwargs(**kwargs)
    run_tool(
        "cutadapt",
        Version.CUTADAPT.value,
        tool_args=cutadapt_args,
        input_name="input.fastq",
        output_name="output.fastq",
        **kwargs
    )

def kraken2(kraken2_args="", **kwargs):
    """Runs Kraken2 via Toolchest.

    (Currently, only single .fastq inputs are supported.)

    :param kraken2_args: (optional) Additional arguments to be passed to Kraken2.
    :param input_path: Path (client-side) of file to be passed in as input.
    :param output_path: Path (client-side) where the output will be downloaded.

    Usage::

        >>> import toolchest_client as tc
        >>> tc.kraken2(
        ...     input_path="./path/to/input",
        ...     output_path="./path/to/output",
        ... )
    """

    _validate_tool_kwargs(**kwargs)
    run_tool(
        "kraken2",
        Version.KRAKEN2.value,
        tool_args=kraken2_args,
        input_name="input.fastq",
        output_name="output.txt",
        **kwargs
    )

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
    :param output_name: Internal name of file outputted by the tool.
    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: Path (client-side) where the output file will be downloaded.
    """

    q = Query()
    q.run_query(tool, version, **kwargs)


def bowtie2(tool_args="", **kwargs):
    """Runs Bowtie 2 (for alignment) via Toolchest.

    :param tool_args: Additional arguments to be passed to Bowtie 2.
    :param database_name: Name of database to use for Bowtie 2 alignment.
    :param database_version: Version of database to use for Bowtie 2 alignment.
    :type database_version: str
    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: Path (client-side) where the output file will be downloaded.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.bowtie2(
        ...     database_name="DB_name",
        ...     database_version="version_number",
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output",
        ... )

    """

    _validate_tool_kwargs(**kwargs)
    run_tool(
        "bowtie2",
        Version.BOWTIE2.value,
        tool_args=tool_args,
        output_name="output.txt",
        **kwargs
    )


def cutadapt(tool_args, **kwargs):
    """Runs Cutadapt via Toolchest.

    (Currently, only single .fastq inputs are supported.)

    :param tool_args: Additional arguments to be passed to Cutadapt.
    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: Path (client-side) where the output file will be downloaded.

    .. note:: Do **NOT** include the output path (`-o output_path`) or the
      input path (`inputs` at the end) in the passed `cutadapt_args`. Inputs
      and outputs will be automatically handled by the Toolchest backend, and
      including these arguments will lead to errors or undesired output.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.cutadapt(
        ...     tool_args="-a AACCGGTT",
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output",
        ... )

    """

    _validate_tool_kwargs(**kwargs)
    run_tool(
        "cutadapt",
        Version.CUTADAPT.value,
        tool_args=tool_args,
        output_name="output.fastq",
        **kwargs
    )

def kraken2(tool_args="", **kwargs):
    """Runs Kraken 2 via Toolchest.

    (Currently, only single .fastq inputs are supported.)

    :param tool_args: (optional) Additional arguments to be passed to Kraken 2.
    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: Path (client-side) where the output will be downloaded.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.kraken2(
        ...     tool_args="",
        ...     inputs="./path/to/input.fastq",
        ...     output_path="./path/to/output.txt",
        ... )
    """

    _validate_tool_kwargs(**kwargs)
    run_tool(
        "kraken2",
        Version.KRAKEN2.value,
        tool_args=tool_args,
        output_name="output.txt",
        **kwargs
    )


def test(tool_args="", **kwargs):
    """Run a test pipeline segment via Toolchest. A plain text file containing 'success' is returned."

    :param tool_args: Additional arguments, present to maintain a consistent interface. This is disregarded.
    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: Path (client-side) where the output file will be downloaded.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.test(
        ...     inputs="./path/to/input.txt",
        ...     output_path="./path/to/output.txt",
        ... )

    """

    _validate_tool_kwargs(**kwargs)
    run_tool(
        "test",
        Version.TEST.value,
        tool_args=tool_args,
        output_name="output.txt",
        **kwargs
    )

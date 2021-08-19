"""
toolchest_client.tools.api
~~~~~~~~~~~~~~~~~~~~~~

This module contains the API for using Toolchest tools.
"""

from toolchest_client.tools import Kraken2, Cutadapt, Bowtie2, STARInstance, Test, Unicycler


def bowtie2(inputs, output_path, database_name, database_version, tool_args=""):
    """Runs Bowtie 2 (for alignment) via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to Bowtie 2.
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

    instance = Bowtie2(
        tool_args=tool_args,
        output_name='output.txt',
        inputs=inputs,
        output_path=output_path,
        database_name=database_name,
        database_version=database_version
    )
    instance.run()


def cutadapt(inputs, output_path, tool_args):
    """Runs Cutadapt via Toolchest.

    (Currently, only single .fastq inputs are supported.)

    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: Path (client-side) where the output file will be downloaded.
    :param tool_args: Additional arguments to be passed to Cutadapt.


    .. note:: Inputs and outputs should be specified in `inputs` and `output_path`.
      These will be automatically handled by the Toolchest backend. Input/output
      arguments supplied in `tool_args` (e.g., `-o`) will be ignored.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.cutadapt(
        ...     tool_args="-a AACCGGTT",
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output",
        ... )

    """

    instance = Cutadapt(
        tool_args=tool_args,
        output_name='output.fastq',
        inputs=inputs,
        output_path=output_path,
    )
    instance.run()


def kraken2(inputs, output_path, database_name="standard", database_version="1", tool_args=""):
    """Runs Kraken 2 via Toolchest.

    (Currently, only single .fastq inputs are supported.)

    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: Path (client-side) where the output will be downloaded.
    :param tool_args: (optional) Additional arguments to be passed to Kraken 2.
    :param database_name: (optional) Name of database to use for Kraken 2 alignment. Defaults to standard DB.
    :param database_version: (optional) Version of database to use for Kraken 2 alignment. Defaults to 1.
    :type database_version: str

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.kraken2(
        ...     tool_args="",
        ...     inputs="./path/to/input.fastq",
        ...     output_path="./path/to/output.txt",
        ... )

    """

    instance = Kraken2(
        tool_args=tool_args,
        output_name='output.txt',
        inputs=inputs,
        output_path=output_path,
        database_name=database_name,
        database_version=database_version,        
    )
    instance.run()


def STAR(output_path, read_one, database_name, database_version="1", read_two=None, tool_args=""):
    """Runs STAR (for alignment) via Toolchest.

    :param database_name: Name of database to use for STAR alignment.
    :param database_version: Version of database to use for STAR alignment (defaults to 1).
    :type database_version: str
    :param tool_args: (optional) Additional arguments to be passed to STAR.
    :param read_one: Path to the file containing single input file, or R1 short reads for paired-end inputs.
    :param read_two: (optional) Path to the file containing R2 short reads for paired-end inputs.
    :param output_path: Path (client-side) where the output file will be downloaded.

    .. note:: Single-read inputs should be supplied in the `read_one` argument by themselves.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.STAR(
        ...     database_name="DB_name",
        ...     read_one="./r1.fastq",
        ...     read_two="./r2.fastq",
        ...     tool_args="--mode bold",
        ...     output_path="scratch"
        ... )

    """

    inputs = [read_one]
    if read_two != None:
        inputs.append(read_two)
    instance = STARInstance(
        tool_args=tool_args,
        output_name='Aligned.out.sam',
        input_prefix_mapping={
            read_one: None,
            read_two: None,
        },
        inputs=inputs,
        output_path=output_path,
        database_name=database_name,
        database_version=database_version,
    )
    instance.run()

def test(inputs, output_path, tool_args=""):
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

    instance = Test(
        tool_args=tool_args,
        output_name='output.txt',
        inputs=inputs,
        output_path=output_path,
    )
    instance.run()


def unicycler(output_path, read_one=None, read_two=None, long_reads=None, tool_args=""):
    """Runs Unicycler (for alignment) via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to Unicycler.
    :param read_one: (optional) Path to the file containing R1 short reads.
    :param read_two: (optional) Path to the file containing R2 short reads.
    :param long_reads: (optional) Path to the file containing long reads.
    :param output_path: Path (client-side) where the output file will be downloaded.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.unicycler(
        ...     read_one="./r1.fastq",
        ...     read_two="./r2.fastq",
        ...     long_reads="./long_reads.fasta",
        ...     tool_args="--mode bold",
        ...     output_path="scratch"
        ... )

    """

    instance = Unicycler(
        tool_args=tool_args,
        output_name='output.txt',
        input_prefix_mapping={
            read_one: "-1",
            read_two: "-2",
            long_reads: "-l",
        },
        inputs=[read_one, read_two, long_reads],
        output_path=output_path,
    )
    instance.run()

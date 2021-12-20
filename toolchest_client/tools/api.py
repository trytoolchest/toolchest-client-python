"""
toolchest_client.tools.api
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the API for using Toolchest tools.
"""
from toolchest_client.files import assert_exists
from toolchest_client.tools import Kraken2, CellRangerMkfastq, Bowtie2, Shi7, ShogunAlign, ShogunFilter, STARInstance, Test, Unicycler


def bowtie2(inputs, output_path, database_name, database_version="1", tool_args=""):
    """Runs Bowtie 2 (for alignment) via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to Bowtie 2.
    :param database_name: Name of database to use for Bowtie 2 alignment.
    :param database_version: (optional) Version of database to use for Bowtie 2 alignment.
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
        output_name='output.tar.gz',
        inputs=inputs,
        output_path=output_path,
        database_name=database_name,
        database_version=database_version
    )
    instance.run()


def cellranger_mkfastq(inputs, output_path, samplesheet_name, tool_args=""):
    """Runs Cell Ranger's mkfastq command via Toolchest.

    :param inputs: Path (client-side) to be passed in as input.
    :param output_path: Path (client-side) where the output file will be downloaded.
    :param samplesheet_name: Name of sample sheet. Expected to exist inside of "inputs".
    :param tool_args: Additional arguments to be passed to Cell Ranger.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.cellranger_mkfastq(
        ...     tool_args="",
        ...     samplesheet_name="sample_sheet.csv",
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output.tar.gz",
        ... )

    """

    # Add --samplesheet arg
    assert_exists(f"{inputs}/{samplesheet_name}")
    tool_args = f"--samplesheet={samplesheet_name} " + tool_args

    instance = CellRangerMkfastq(
        tool_args=tool_args,
        output_name='output',
        inputs=inputs,
        output_path=output_path,
    )
    instance.run()


def kraken2(output_path, inputs=[], database_name="standard", database_version="1",
            tool_args="", read_one=None, read_two=None):
    """Runs Kraken 2 via Toolchest.

    :param inputs: Path or list of paths (client-side) to be passed in as input(s).
    :param output_path: Path (client-side) where the output will be downloaded.
    :param tool_args: (optional) Additional arguments to be passed to Kraken 2.
    :param database_name: (optional) Name of database to use for Kraken 2 alignment. Defaults to standard DB.
    :param database_version: (optional) Version of database to use for Kraken 2 alignment. Defaults to 1.
    :type database_version: str
    :param read_one: (optional) Path to read 1 of paired-read input files.
    :param read_two: (optional) Path to read 2 of paired-read input files.

    .. note:: Paired-read inputs can be provided either through `inputs` or
     through `read_one` and `read_two`.

     If using `inputs`, use a list of two filepaths: `inputs=['/path/to/read_1', '/path_to/read_2']`

     If using `read_one` and `read_two`, these will be interpreted as the input files
     over anything given in `inputs`.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.kraken2(
        ...     tool_args="",
        ...     inputs="./path/to/input.fastq",
        ...     output_path="./path/to/output.txt",
        ... )

    """

    if read_one:
        inputs = [read_one]
        if read_two:
            inputs.append(read_two)

    # Add --paired tag if paired reads are provided. Else, remove if present.
    tool_args_list = tool_args.split()
    if len(inputs) == 2:
        if "--paired" not in tool_args_list:
            if not tool_args:
                tool_args = "--paired"
            else:
                tool_args = "--paired " + tool_args
    else:
        if "--paired" in tool_args_list:
            tool_args = tool_args_list.remove("--paired").join(" ")

    instance = Kraken2(
        tool_args=tool_args,
        output_name='output.tar.gz',
        inputs=inputs,
        output_path=output_path,
        database_name=database_name,
        database_version=database_version,
    )
    instance.run()


def shi7(inputs, output_path, tool_args=""):
    """Runs shi7 via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to shi7.
    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: Path (client-side) where the output file will be downloaded.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.shi7(
        ...     inputs="./path/to/fastq/",
        ...     output_path="./path/to/output.txt", # todo: fix for multiple output files
        ... )

    """

    instance = Shi7(
        tool_args=tool_args,
        output_name='output.tar.gz',
        inputs=inputs,
        output_path=output_path,
    )
    instance.run()


def shogun_align(inputs, output_path, database_name="shogun_standard", database_version="1", tool_args=""):
    """Runs Shogun (for alignment) via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to Shogun.
    :param database_name: (optional) Name of database to use for Shogun alignment. Defaults to the pre-built DB files at https://github.com/knights-lab/SHOGUN.
    :param database_version: (optional) Version of database to use for Shogun alignment.
    :type database_version: str
    :param inputs: Path to be passed in as input.
    :param output_path: Path (client-side) where the output files will be downloaded.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.shogun_align(
        ...     database_name="DB_name",
        ...     database_version="version_number",
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output",
        ... )

    """

    instance = ShogunAlign(
        tool_args=tool_args,
        output_name='output.tar.gz',
        inputs=inputs,
        output_path=output_path,
        database_name=database_name,
        database_version=database_version
    )
    instance.run()


def shogun_filter(inputs, output_path, database_name="shogun_standard", database_version="1", tool_args=""):
    """Runs Shogun (for filtering human genome content) via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to Shogun.
    :param database_name: (optional) Name of database to use for Shogun alignment. Defaults to the pre-built DB files at https://github.com/knights-lab/SHOGUN.
    :param database_version: (optional) Version of database to use for Shogun alignment.
    :type database_version: str
    :param inputs: Path to be passed in as input.
    :param output_path: Path (client-side) where the output files will be downloaded.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.shogun_filter(
        ...     database_name="DB_name",
        ...     database_version="version_number",
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output",
        ... )

    """

    instance = ShogunFilter(
        tool_args=tool_args,
        output_name='output.tar.gz',
        inputs=inputs,
        output_path=output_path,
        database_name=database_name,
        database_version=database_version
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
        output_name='output.tar.gz',
        input_prefix_mapping={
            read_one: "-1",
            read_two: "-2",
            long_reads: "-l",
        },
        inputs=[read_one, read_two, long_reads],
        output_path=output_path,
    )
    instance.run()

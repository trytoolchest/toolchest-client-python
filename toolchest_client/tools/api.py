"""
toolchest_client.tools.api
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the API for using Toolchest tools.
"""
from datetime import date
from toolchest_client.tools import AlphaFold, Bowtie2, CellRangerCount, ClustalO, DiamondBlastp, DiamondBlastx, Demucs,\
    Kraken2, Megahit, Rapsearch2, Shi7, ShogunAlign, ShogunFilter, STARInstance, Test, Unicycler


def alphafold(inputs, output_path=None, model_preset=None, max_template_date=None, use_reduced_dbs=False,
              is_prokaryote_list=None, **kwargs):
    """Runs AlphaFold via Toolchest.

    :param model_preset: (optional) Allows you to choose a specific AlphaFold model from
        [monomer, monomer_casp14, monomer_ptm, multimer]. Default mode if not provided is monomer.
    :param max_template_date: (optional) Allows for predicting structure of protiens already in the database by setting
        a date before it was added in YYYY-MM-DD format. Will use today's date if not provided.
    :param use_reduced_dbs: (optional) Uses a smaller version of the BFD database that will reduce run time at the cost
        result quality.
    :type is_prokaryote_list: (optional) takes a list of booleans that determine whether all input sequences in the
        given fasta file are prokaryotic. Expects the string that would normally input into AlphaFold (e.g. "true,true"
        if there are two prokaryote inputs)
    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: (optional) Path to directory where the output file(s) will be downloaded

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.alphafold(
        ...     model_preset="monomer",
        ...     max_template_date="2022-01-04",
        ...     use_reduced_dbs=True,
        ...     is_prokaryote_list=[True],
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output",
        ... )

    """
    tool_args = (
        (f"--model_preset={model_preset} " if model_preset is not None else "") +
        (f"--max_template_date={max_template_date} " if max_template_date is not None
         else f"--max_template_date={date.today().strftime('%Y-%m-%d')} ") +
        (f"--is_prokaryote_list={is_prokaryote_list} " if is_prokaryote_list is not None else "") +
        ("--db_preset=reduced_dbs " if use_reduced_dbs else "")
    )
    instance = AlphaFold(
        inputs=inputs,
        output_path=output_path,
        tool_args=tool_args,
        **kwargs,
    )
    output = instance.run()
    return output


def bowtie2(inputs, output_path=None, database_name="GRCh38_noalt_as", database_version="1", tool_args="", **kwargs):
    """Runs Bowtie 2 (for alignment) via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to Bowtie 2.
    :param database_name: (optional) Name of database to use for Bowtie 2 alignment. Uses the GRCh38 no-alt analysis set
        ("GRCh38_noalt_as") by default. Index files generated by the Langmead lab.
    :param database_version: (optional) Version of database to use for Bowtie 2 alignment.
    :type database_version: str
    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: (optional) Path (client-side) where the output file will be downloaded.

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
        database_version=database_version,
        **kwargs,
    )
    output = instance.run()
    return output


def cellranger_count(inputs, database_name="GRCh38", output_path=None, tool_args="", **kwargs):
    """Runs Cell Ranger's count command via Toolchest.

    This tool is only available to users who already have a license to use Cell Ranger.

    :param inputs: Path (client-side) to a directory of input FASTQ files that will be passed in as input.
    :param output_path: (optional) Path (client-side) where the output file will be downloaded.
    :param database_name: Name of transcriptome (reference genome database). Defaults to `GRCh38`.
    :param tool_args: Additional arguments to be passed to Cell Ranger.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.cellranger_count(
        ...     tool_args="",
        ...     database_name="GRCh38",
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output",
        ... )

    """

    # Note: all cellranger transcriptomes are registered as "cellranger_{name}" in the API
    database_name = "cellranger_" + database_name

    instance = CellRangerCount(
        tool_args=tool_args,
        output_name='output.tar.gz',
        inputs=inputs,
        output_path=output_path,
        database_name=database_name,
        database_version="2020",
        **kwargs,
    )
    output = instance.run()
    return output


def clustalo(inputs, output_path=None, tool_args="", **kwargs):
    """Runs Clustal Omega via Toolchest.

    :param inputs: Path (client-side) to a FASTA file that will be passed in as input.
    :param output_path: (optional) Path (client-side) where the output file will be downloaded.
    :param tool_args: Additional arguments to be passed to Clustal Omega.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.clustalo(
        ...     tool_args="",
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output.fasta",
        ... )

    """

    instance = ClustalO(
        tool_args=tool_args,
        output_name='output.tar.gz',
        inputs=inputs,
        output_path=output_path,
        **kwargs,
    )
    output = instance.run()
    return output


def diamond_blastp(inputs, output_path=None, tool_args="", **kwargs):
    """Runs diamond blastp via Toolchest.

      :param inputs: Path to a file that will be passed in as input. FASTA or FASTQ formats are supported (it may be
        gzip compressed)
      :param output_path: (optional) File path where the output will be downloaded. Log file (diamond.log) will be
        downloaded in the same directory as the out file
      :param tool_args: Additional arguments to be passed to demucs.

      Usage::

          >>> import toolchest_client as toolchest
          >>> toolchest.diamond_blastp(
          ...     tool_args="",
          ...     inputs="./path/to/input.fa",
          ...     output_path="./path/to/output/out_file.tsv",
          ... )

      """
    instance = DiamondBlastp(
        inputs=inputs,
        output_name='output.tar.gz',
        output_path=output_path,
        tool_args=tool_args,
        **kwargs,
    )
    output = instance.run()
    return output


def diamond_blastx(inputs, output_path=None, tool_args="", **kwargs):
    """Runs diamond blastx via Toolchest.
      :param inputs: Path to a file that will be passed in as input. FASTA or FASTQ formats are supported (it may be
        gzip compressed)
      :param output_path: (optional) File path where the output will be downloaded. Log file (diamond.log) will be
        downloaded in the same directory as the out file
      :param tool_args: Additional arguments to be passed to demucs.
      Usage::
          >>> import toolchest_client as toolchest
          >>> toolchest.diamond_blastp(
          ...     tool_args="",
          ...     inputs="./path/to/input.fa",
          ...     output_path="./path/to/output/out_file.tsv",
          ... )
      """
    instance = DiamondBlastx(
        inputs=inputs,
        output_name='output.tar.gz',
        output_path=output_path,
        tool_args=tool_args,
        **kwargs,
    )
    output = instance.run()
    return output


def demucs(inputs, output_path=None, tool_args="", **kwargs):
    """Runs demucs via Toolchest.

    :param inputs: Path to a file that will be passed in as input. All formats supported by ffmpeg are allowed.
    :param output_path: (optional) Path where the output will be downloaded.
    :param tool_args: Additional arguments to be passed to demucs.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.demucs(
        ...     tool_args="",
        ...     inputs="./path/to/input.wav",
        ...     output_path="./path/to/output/",
        ... )

    """

    instance = Demucs(
        tool_args=tool_args,
        output_name='output.tar.gz',
        inputs=inputs,
        output_path=output_path,
        **kwargs,
    )
    output = instance.run()
    return output


def kraken2(output_path=None, inputs=[], database_name="standard", database_version="1",
            tool_args="", read_one=None, read_two=None, custom_database_path=None, **kwargs):
    """Runs Kraken 2 via Toolchest.

    :param inputs: Path or list of paths (client-side) to be passed in as input(s).
    :param output_path: (optional) Path (client-side) where the output will be downloaded.
    :param tool_args: (optional) Additional arguments to be passed to Kraken 2.
    :param database_name: (optional) Name of database to use for Kraken 2 alignment. Defaults to standard DB.
    :param database_version: (optional) Version of database to use for Kraken 2 alignment. Defaults to 1.
    :type database_version: str
    :param custom_database_path: (optional) Path to a custom database.
    This must be an AWS S3 URI accessible from Toolchest.
    :param read_one: (optional) Path to read 1 of paired-read input files.
    :param read_two: (optional) Path to read 2 of paired-read input files.

    .. note:: Paired-read inputs can be provided either through `inputs` or
     through `read_one` and `read_two`.

     If using `inputs`, use a list of two filepaths: `inputs=['/path/to/read_1', '/path_to/read_2']`

     If using `read_one` and `read_two`, these will be interpreted as the input files
     over anything given in `inputs`.

     If using `custom_database_path`, the given database will supersede any database
     selected via `database_name` and `database_version`.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.kraken2(
        ...     tool_args="",
        ...     inputs="./path/to/input.fastq",
        ...     output_path="./path/to/output",
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
        custom_database_path=custom_database_path,
        **kwargs,
    )
    output = instance.run()
    return output


def megahit(output_path=None, tool_args="", read_one=None, read_two=None, interleaved=None,
            single_end=None, **kwargs):
    """Runs Megahit via Toolchest.

    :param output_path: (optional) Path (client-side) where the output will be downloaded.
    :param tool_args: (optional) Additional arguments to be passed to Megahit.
    :param read_one: (optional) `-1` inputs. Path or list of paths for read 1 of paired-read input files.
    :param read_two: (optional) `-2` inputs. Path or list of paths for read 2 of paired-read input files.
    :param interleaved: (optional) `--12` inputs. Path or list of paths for interleaved paired-end files.
    :param single_end: (optional) `-r` inputs. Path or list of paths for single-end inputs.

    .. note:: Each read in `read_one` should match with a read in `read_two`, and vice
    versa. In other words, the nth read in `read_one` should be paired with the nth read
    in `read_two`.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.megahit(
        ...     tool_args="",
        ...     read_one=["./pair_1/r1.fa", "./pair_2/r1.fa"],
        ...     read_two=["./pair_1/r2.fa", "./pair_2/r2.fa"],
        ...     output_path="./path/to/output",
        ... )

    """

    # If input parameters are lists, parse these for input_prefix_mapping.
    tag_to_param_map = {
        "-1": read_one,
        "-2": read_two,
        "--12": interleaved,
        "-r": single_end,
    }
    input_list = []  # list of all inputs
    input_prefix_mapping = {}  # map of each input to its respective tag
    for tag, param in tag_to_param_map.items():
        if isinstance(param, list):
            for index, input_file in enumerate(param):
                input_list.append(input_file)
                input_prefix_mapping[input_file] = {
                    "prefix": tag,
                    "order": index,
                }
        elif isinstance(param, str):
            input_list.append(param)
            input_prefix_mapping[param] = {
                "prefix": tag,
                "order": 0,
            }

    instance = Megahit(
        tool_args=tool_args,
        output_name='output.tar.gz',
        input_prefix_mapping=input_prefix_mapping,
        inputs=input_list,
        output_path=output_path,
        **kwargs,
    )
    output = instance.run()
    return output


def rapsearch2(inputs, output_path=None, database_name="rapsearch2_seqscreen", database_version="1",
              tool_args="", **kwargs):
    """Runs Rapsearch 2 via Toolchest.
    :param inputs: Path to a FASTA/FASTQ file that will be passed in as input.
    :param output_path: (optional) Base path to where the output file(s) will be downloaded.
    (Functions the same way as the "-o" tag for Rapsearch.)
    :param tool_args: (optional) Additional arguments to be passed to Rapsearch 2.
    :param database_name: (optional) Name of database to use for Rapsearch 2 alignment. Defaults to standard DB.
    :param database_version: (optional) Version of database to use for Rapsearch 2 alignment. Defaults to 1.
    :type database_version: str
    Usage::
        >>> import toolchest_client as toolchest
        >>> toolchest.rapsearch(
        ...     tool_args="",
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output/base",  # outputs
        ... )
    """

    instance = Rapsearch2(
        tool_args=tool_args,
        output_name='output.tar.gz',
        database_name=database_name,
        database_version=database_version,
        inputs=inputs,
        output_path=output_path,
        **kwargs,
    )
    output = instance.run()
    return output


# Adds rapsearch as an alias for rapsearch2
rapsearch = rapsearch2


def shi7(inputs, output_path=None, tool_args="", **kwargs):
    """Runs shi7 via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to shi7.
    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: (optional) Path (client-side) where the output file will be downloaded.
    :return: An Output object, containing info about the output file's location in cloud and/or local storage.

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
        **kwargs,
    )
    output = instance.run()
    return output


def shogun_align(inputs, output_path=None, database_name="shogun_standard", database_version="1", tool_args="",
                 **kwargs):
    """Runs Shogun (for alignment) via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to Shogun.
    :param database_name: (optional) Name of database to use for Shogun alignment. Defaults to the pre-built DB files at https://github.com/knights-lab/SHOGUN. # noqa: E501
    :param database_version: (optional) Version of database to use for Shogun alignment.
    :type database_version: str
    :param inputs: Path to be passed in as input.
    :param output_path: (optional) Path (client-side) where the output file will be downloaded.
    :return: An Output object, containing info about the output file's location in cloud and/or local storage.

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
        database_version=database_version,
        **kwargs,
    )
    output = instance.run()
    return output


def shogun_filter(inputs, output_path=None, database_name="shogun_standard", database_version="1", tool_args="",
                  **kwargs):
    """Runs Shogun (for filtering human genome content) via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to Shogun.
    :param database_name: (optional) Name of database to use for Shogun alignment. Defaults to the pre-built DB files at https://github.com/knights-lab/SHOGUN. # noqa: E501
    :param database_version: (optional) Version of database to use for Shogun alignment.
    :type database_version: str
    :param inputs: Path to be passed in as input.
    :param output_path: (optional) Path (client-side) where the output file will be downloaded.
    :return: An Output object, containing info about the output file's location in cloud and/or local storage.

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
        database_version=database_version,
        **kwargs,
    )
    output = instance.run()
    return output


def STAR(read_one, database_name="GRCh38", output_path=None, database_version="1", read_two=None, tool_args="",
         parallelize=False, **kwargs):
    """Runs STAR (for alignment) via Toolchest.

    :param database_name: Name of database to use for STAR alignment (defaults to GRCh38).
    :param database_version: Version of database to use for STAR alignment (defaults to 1).
    :type database_version: str
    :param tool_args: (optional) Additional arguments to be passed to STAR.
    :param read_one: Path to the file containing single input file, or R1 short reads for paired-end inputs.
    :param read_two: (optional) Path to the file containing R2 short reads for paired-end inputs.
    :param output_path: (optional) Path (client-side) where the output file will be downloaded.
    :param parallelize: (optional) Allow parallelization of STAR if needed.

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
    if read_two is not None:
        inputs.append(read_two)
    instance = STARInstance(
        tool_args=tool_args,
        output_name="Aligned.out.sam" if parallelize else "output.tar.gz",
        input_prefix_mapping={
            read_one: None,
            read_two: None,
        },
        inputs=inputs,
        output_path=output_path,
        database_name=database_name,
        database_version=database_version,
        parallelize=parallelize,
        **kwargs,
    )
    output = instance.run()
    return output


def test(inputs, output_path=None, tool_args="", **kwargs):
    """Run a test pipeline segment via Toolchest. A plain text file containing 'success' is returned."

    :param tool_args: Additional arguments, present to maintain a consistent interface. This is disregarded.
    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: (optional) Path (client-side) where the output file will be downloaded.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.test(
        ...     inputs="./path/to/input.txt",
        ...     output_path="./path/to/output.txt",
        ... )

    """

    instance = Test(
        tool_args=tool_args,
        output_name='output.tar.gz',
        inputs=inputs,
        output_path=output_path,
        **kwargs,
    )
    output = instance.run()
    return output


def unicycler(output_path=None, read_one=None, read_two=None, long_reads=None, tool_args="", **kwargs):
    """Runs Unicycler (for alignment) via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to Unicycler.
    :param read_one: (optional) Path to the file containing R1 short reads.
    :param read_two: (optional) Path to the file containing R2 short reads.
    :param long_reads: (optional) Path to the file containing long reads.
    :param output_path: (optional) Path (client-side) where the output file will be downloaded.

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
        output_name="output.tar.gz",
        input_prefix_mapping={
            read_one: {"prefix": "-1"},
            read_two: {"prefix": "-2"},
            long_reads: {"prefix": "-l"},
        },
        inputs=[read_one, read_two, long_reads],
        output_path=output_path,
        **kwargs,
    )
    output = instance.run()
    return output

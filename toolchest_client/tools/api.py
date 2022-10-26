"""
toolchest_client.tools.api
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the API for using Toolchest tools.
"""
import json
import os.path
from datetime import date

from toolchest_client.api.exceptions import ToolchestException
from toolchest_client.api.instance_type import InstanceType
from toolchest_client.files import path_is_s3_uri
from toolchest_client.tools import AlphaFold, BLASTN, Bowtie2, Bracken, CellRangerCount, ClustalO, Demucs, \
    DiamondBlastp, DiamondBlastx, FastQC, HUMAnN3, Jupyter, Kallisto, Kraken2, Lastal5, Lug, MetaPhlAn, Megahit, \
    Python3, Rapsearch2, Salmon, Shi7, ShogunAlign, ShogunFilter, STARInstance, Transfer, Test, Unicycler
from toolchest_client.tools.humann import HUMAnN3Mode


def alphafold(inputs, output_path=None, model_preset=None, max_template_date=None, use_reduced_dbs=False,
              is_prokaryote_list=None, **kwargs):
    """Runs AlphaFold via Toolchest.

    :param model_preset: (optional) Allows you to choose a specific AlphaFold model from
        [monomer, monomer_casp14, monomer_ptm, multimer]. Default mode if not provided is monomer.
    :param max_template_date: (optional) Allows for predicting structure of protiens already in the database by setting
        a date before it was added in YYYY-MM-DD format. Will use today's date if not provided.
    :param use_reduced_dbs: (optional) Uses a smaller version of the BFD database that will reduce run time at the cost
        of result quality.
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
    if 'instance_type' in kwargs:
        raise ToolchestException("Argument 'instance_type' is not supported by Alphafold currently.")
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


def blastn(inputs, output_path=None, database_name="blastn_nt", database_version="1", tool_args="",
           output_primary_name="blastn_results.out", **kwargs):
    """Runs BLASTN via Toolchest.

    :param inputs: Path to a file that will be passed in as input. Only FASTA formats are supported.
    :param database_name: (optional) Name of database to use for BLASTN.
    :param database_version: (optional) Version of database to use for BLASTN.
    :param output_path: (optional) (optional) Path to directory where the output file(s) will be downloaded.
    :param output_primary_name: (optional) Base name of output file.
    :param tool_args: Additional arguments to be passed to BLASTN.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.blastn(
        ...     inputs="./path/to/input.fna",
        ...     output_path="./path/to/output/",
        ...     database_name="nt",
        ...     tool_args="",
        ... )

      """
    instance = BLASTN(
        inputs=inputs,
        output_path=output_path,
        output_primary_name=output_primary_name,
        database_name=database_name,
        database_version=database_version,
        tool_args=tool_args,
        **kwargs,
    )
    output = instance.run()
    return output


def bracken(kraken2_report, output_path=None, database_name="standard", database_version="1",
            tool_args="", output_primary_name="output.bracken", remote_database_path=None, **kwargs):
    """Runs Bracken via Toolchest.

    :param kraken2_report: Path to the Kraken 2 output file to be used..
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
    :param output_primary_name: (optional) Name of Bracken output file. Defaults to output.bracken
    :param tool_args: (optional) Additional arguments to be passed to Kraken 2.
    :param database_name: (optional) Name of database that was used for Kraken 2 alignment. Defaults to standard.
    :param database_version: (optional) Version of database that was used for Kraken 2 alignment. Defaults to 1.
    :param remote_database_path: (optional) Path to remote database that was used with Kraken 2. Overrides other DBs.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.bracken(
        ...     inputs="./path/to/input.fastq",
        ...     output_path="./path/to/output",
        ...     tool_args="-r 150 -l G -t 10",
        ... )

    """

    instance = Bracken(
        tool_args=tool_args,
        inputs=kraken2_report,
        output_path=output_path,
        output_primary_name=output_primary_name,
        database_name=database_name,
        database_version=database_version,
        remote_database_path=remote_database_path,
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
    :param output_path: (optional) Path to directory where the output file(s) will be downloaded

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
        inputs=inputs,
        output_path=output_path,
        database_name=database_name,
        database_version="2020",
        **kwargs,
    )
    output = instance.run()
    return output


def clustalo(inputs, output_path=None, output_primary_name=None, tool_args="", **kwargs):
    """Runs Clustal Omega via Toolchest.

    :param inputs: Path (client-side) to a FASTA file that will be passed in as input.
    :param output_path: (optional) Path to directory where the output file(s) will be downloaded.
    :param output_primary_name: (optional) Base name of output file.
    :param tool_args: Additional arguments to be passed to Clustal Omega.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.clustalo(
        ...     tool_args="",
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output",
        ...     output_primary_name="output.fasta",
        ...     # primary output file will be downloaded to ./path/to/output/output.fasta
        ... )

    """

    instance = ClustalO(
        tool_args=tool_args,
        inputs=inputs,
        output_path=output_path,
        output_primary_name=output_primary_name,
        **kwargs,
    )
    output = instance.run()
    return output


def demucs(inputs, output_path=None, tool_args="", **kwargs):
    """Runs demucs via Toolchest.

    :param inputs: Path to a file that will be passed in as input. All formats supported by ffmpeg are allowed.
    :param output_path: (optional) Path to directory where the output file(s) will be downloaded.
    :param tool_args: Additional arguments to be passed to demucs.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.demucs(
        ...     tool_args="",
        ...     inputs="./path/to/input.wav",
        ...     output_path="./path/to/output/",
        ... )

    """
    if 'instance_type' in kwargs:
        raise ToolchestException("Argument 'instance_type' is not supported by Demucs currently.")

    instance = Demucs(
        tool_args=tool_args,
        inputs=inputs,
        output_path=output_path,
        **kwargs,
    )
    output = instance.run()
    return output


def diamond_blastp(inputs, output_path=None, database_name="diamond_blastp_standard", database_version="1",
                   output_primary_name="out_file.tsv", tool_args="", remote_database_path=None,
                   remote_database_primary_name=None, **kwargs):
    """Runs diamond blastp via Toolchest.

    :param inputs: Path to a file that will be passed in as input. FASTA or FASTQ formats are supported (it may be
    gzip compressed)
    :param database_name: (optional) Name of database to use for DIAMOND BLASTP.
    :param database_version: (optional) Version of database to use for DIAMOND BLASTP.
    :param output_path: (optional) (optional) Path to directory where the output file(s) will be downloaded.
    Log file (diamond.log) will be downloaded in the same directory as the out file(s).
    :param output_primary_name: (optional) Base name of output file.
    :param remote_database_path: (optional) Path to a custom database.
    This must be an AWS S3 URI accessible by Toolchest.
    :param remote_database_primary_name: Name or path of the file to use as the primary database file
        (i.e., what you would pass into the command line as the database), if uploading multiple
        files. If unspecified, assumes that the *directory* of files is what will be passed in
        as the database.
    :param tool_args: Additional arguments to be passed to diamond blastp.

    If using `remote_database_path`, the given database will supersede any database
     selected via `database_name` and `database_version`.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.diamond_blastp(
        ...     tool_args="",
        ...     inputs="./path/to/input.fa",
        ...     output_path="./path/to/output/",
        ...     output_primary_name="out_file.tsv",
        ... )

      """
    instance = DiamondBlastp(
        inputs=inputs,
        output_path=output_path,
        remote_database_path=remote_database_path,
        remote_database_primary_name=remote_database_primary_name,
        database_name=database_name,
        database_version=database_version,
        output_primary_name=output_primary_name,
        tool_args=tool_args,
        **kwargs,
    )
    output = instance.run()
    return output


def diamond_blastx(inputs, output_path=None, database_name="diamond_blastx_standard", database_version="1",
                   output_primary_name="out_file.tsv", tool_args="", distributed=False, remote_database_path=None,
                   **kwargs):
    """Runs diamond blastx via Toolchest.
    :param inputs: Path to a file that will be passed in as input. FASTA or FASTQ formats are supported (it may be
gzip compressed)
    :param database_name: (optional) Name of database to use for DIAMOND BLASTX.
    :param database_version: (optional) Version of database to use for DIAMOND BLASTX.
    :param output_path: (optional) (optional) Path to directory where the output file(s) will be downloaded.
    Log file (diamond.log) will be downloaded in the same directory as the out file(s).
    :param output_primary_name: (optional) Base name of output file.
    :param remote_database_path: (optional) Path to a custom database.
    This must be an AWS S3 URI accessible by Toolchest.
    :param tool_args: (optional) Additional arguments to be passed to diamond blastx.
    :param distributed: (optional) Distribute DIAMOND BLASTX. Note that this is non-deterministic, and might change
    results.

    If using `remote_database_path`, the given database will supersede any database
     selected via `database_name` and `database_version`.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.diamond_blastx(
        ...     tool_args="",
        ...     inputs="./path/to/input.fa",
        ...     output_path="./path/to/output/",
        ...     output_primary_name="out_file.tsv",
        ... )

      """
    instance = DiamondBlastx(
        inputs=inputs,
        remote_database_path=remote_database_path,
        database_name=database_name,
        database_version=database_version,
        output_path=output_path,
        output_primary_name=output_primary_name,
        tool_args=tool_args,
        distributed=distributed,
        **kwargs,
    )
    output = instance.run()
    return output


def fastqc(inputs, output_path=None, tool_args="", contaminants="", adapters="", limits="", **kwargs):
    """Runs FastQC via Toolchest.

    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
    :param tool_args: (optional) Additional arguments to be passed to FastQC.
    :param contaminants: (optional) Path to a file to specify the list of contaminants to screen overrepresented
    sequences against.
    :param adapters: (optional) Path to a file to specify the list of adapter sequences which will be explicity searched
    against the library
    :param limits: (optional) Path to a file that the contains a set of criteria which will be used to determine the
    warn/error limits for the various modules

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.fastqc(
        ...     inputs="./path/to/file.fastq",
        ...     output_path="./path/to/directory/",
        ... )

    """
    input_prefix_mapping = {}
    if isinstance(inputs, str):
        inputs = [inputs]
    for i in inputs:
        input_prefix_mapping[i] = {
            "prefix": "",
        }
    if contaminants:
        inputs.append(contaminants)
        input_prefix_mapping[contaminants] = {
            "prefix": "-c",
        }
    if adapters:
        inputs.append(adapters)
        input_prefix_mapping[adapters] = {
            "prefix": "-a",
        }
    if limits:
        inputs.append(limits)
        input_prefix_mapping[limits] = {
            "prefix": "-l",
        }
    instance = FastQC(
        tool_args=tool_args,
        inputs=inputs,
        output_path=output_path,
        **kwargs,
    )
    output = instance.run()
    return output


def humann3(inputs, output_path=None, tool_args="", mode=HUMAnN3Mode.HUMANN,
            taxonomic_profile=None, input_pathways=None, output_primary_name=None, **kwargs):
    """Runs HUMAnN 3 via Toolchest.

    Uses the ChocoPhlAn and UniRef databases packaged with HUMAnN.

    :param inputs: Path to a *single* file that will be passed in as input. FASTA and FASTQ formats are supported (it
may be gzip compressed). SAM/BAM and M8 inputs are also supported (non-compressed).
    :param output_path: (optional) Path to directory where the output file(s) will be downloaded.
    :param tool_args: (optional) Additional arguments to be passed to HUMAnN.
    :param mode: (optional) Enum to allow for the exemution of humann3 utility scripts. Defaults to executing humann.
    :param taxonomic_profile: (optional) Path to a MetaPhlAn output tsv (taxonomic profile). Speeds up execution if
provided.
    :param input_pathways: (optional) Path to input pathways from a standard humann run for use with
"humann_unpack_pathways".
    :param output_primary_name: (optional) The name of the output file if the mode outputs a file.

    Note: Paired-end inputs should be concatenated and passed in as a single input file before
    running HUMAnN 3.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.humann3(
        ...     tool_args="",
        ...     inputs="./path/to/input.fa",
        ...     output_path="./path/to/output/",
        ...     output_primary_name="out_file.tsv",
        ... )

      """
    if isinstance(inputs, list) and len(inputs) > 1:
        print("Multiple inputs detected. Following HUMAnN 3 recommendations, paired-end files should be concatenated "
              "before being passed in as input.")
        print("To run the files individually, use a separate humann3 function call for each input.")
        raise ToolchestException("humann3 only supports single input files.")
    elif isinstance(inputs, list):
        inputs = inputs[0]
    if mode.value[1] and output_primary_name is None:
        print('WARNING: No output_primary_name provided to mode that requires one. Using "output.tsv" as a default.')
        output_primary_name = "output.tsv"
    elif not mode.value[1] and output_primary_name is not None:
        print(f'WARNING: No output_primary_name should be set for mode: {mode.value[0]}, as it outputs to a directory. '
              'Removing output_primary_name to continue execution.')
        output_primary_name = None

    tool_args = " ".join([mode.value[0], tool_args])
    input_prefix_mapping = {
        inputs: {
            "prefix": "--input",
            "order": 0,
        }
    }

    if mode == HUMAnN3Mode.HUMANN and taxonomic_profile is not None:
        input_prefix_mapping[taxonomic_profile] = {
            "prefix": "--taxonomic-profile",
            "order": 1
        }
        inputs = [inputs, taxonomic_profile]
    elif taxonomic_profile is not None:
        raise ToolchestException(f"Taxonomic profile is only supported for {HUMAnN3Mode.HUMANN.value} mode.")

    if mode == HUMAnN3Mode.HUMANN_UNPACK_PATHWAYS and input_pathways is not None:
        input_prefix_mapping[inputs]["prefix"] = "--input-genes"
        input_prefix_mapping[input_pathways] = {
            "prefix": "--input-pathways",
            "order": 1
        }
        inputs = [inputs, input_pathways]
    elif input_pathways is not None:
        raise ToolchestException(f"Input pathways is only supported for {HUMAnN3Mode.HUMANN_UNPACK_PATHWAYS.value} "
                                 "mode.")
    instance = HUMAnN3(
        inputs=inputs,
        input_prefix_mapping=input_prefix_mapping,
        output_primary_name=output_primary_name,
        output_path=output_path,
        tool_args=tool_args,
        **kwargs,
    )
    output = instance.run()
    return output


def jupyter(notebook, inputs=None, output_path=None, requirements=None,
            version_tag="latest", grace_period_seconds=None, port=None, **kwargs):
    """Get a spawn token for a Jamsocket Jupyter notebook environment via toolchest.

    :param notebook: path to the Jupyter Notebook to run on environment start.
    :param inputs: (optional) path(s) to the files that will be accessible in the spawned environment. Additional
    Jupyter Notebooks can be provided here.
    :param requirements: (optional) path to a pip requirements.txt file to install dependencies for the notebook
    environment.
    :param output_path: (optional) local path to where the output file(s) will be downloaded.
    :param version_tag: (optional) the docker tag used to version the notebook env. "latest" will be used if a tag is
    not provided.
    :param grace_period_seconds: (optional) grace period (in seconds) to wait after last connection is closed before
    shutting down the notebook
    :param port: (optional) a port that will be open on the notebook
    usage::
        >>> import toolchest_client as toolchest
        >>> toolchest.jupyter(
        ...     notebook="./path/to/notebook.ipynb",
        ...     inputs=["./path/to/file.txt", "./path/to/other_notebook.ipynb"],
        ...     requirements="./path/to/requirements.txt",
        ...     output_path="./path/to/local/output/",
        ...     version_tag="v1",
        ...     grace_period_seconds="300",
        ...     port="8080",
        ... )
    """
    tool_args = {
        "docker-tag": version_tag,
        "jamsocket-args": {
            "tag": version_tag,
        }
    }
    if grace_period_seconds is not None:
        tool_args["jamsocket-args"]["grace_period_seconds"] = grace_period_seconds
    if port is not None:
        tool_args["jamsocket-args"]["port"] = port
    if inputs is None:
        inputs = []
    if type(inputs) is str:
        inputs = [inputs]
    input_prefix_mapping = {
        notebook: {
            "prefix": "notebook",
        }
    }
    for i in inputs:
        input_prefix_mapping[i] = {
            "prefix": "",
        }
    inputs.append(notebook)
    if requirements is not None:
        input_prefix_mapping[requirements] = {
            "prefix": "requirements",
        }
        inputs.append(requirements)
    instance = Jupyter(
        tool_args=json.dumps(tool_args),
        inputs=inputs,
        input_prefix_mapping=input_prefix_mapping,
        output_path=output_path,
        **kwargs,
    )
    output = instance.run()
    return output


def kallisto(output_path=None, inputs=[], database_name="kallisto_homo_sapiens", database_version="1",
             tool_args="", gtf=None, chromosomes=None, **kwargs):
    """Runs Kallisto quant via Toolchest.

    :param inputs: Path or list of paths (client-side) to be passed in as input(s).
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
    :param tool_args: (optional) Additional arguments to be passed to Kallisto.
    :param database_name: (optional) Name of database to use for Kallisto alignment. Defaults to the Homo sapiens DB.
    :param database_version: (optional) Version of database to use for Kallisto alignment. Defaults to 1.
    :type database_version: str
    :param gtf: (optional) path to a GTF file for transcriptome information (required for --genomebam).
    :param chromosomes: (optional) Path to a tab separated file with chromosome names and lengths.

    .. note:: Single-end read inputs require --single, --fragment-length (or -l), and --sd (or -s) to be provided via
    tool_args

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.kallisto(
        ...     tool_args="",
        ...     inputs=["./path/to/input_r1.fastq", "./path/to/input_r2.fastq"],
        ...     output_path="./path/to/output",
        ... )

    """

    input_prefix_mapping = {}  # map of each input to its respective tag
    index = 0
    if gtf:
        input_prefix_mapping[gtf] = {
            "prefix": "--gtf",
            "order": index
        }
        index += 1
    if chromosomes:
        input_prefix_mapping[gtf] = {
            "prefix": "--chromosomes",
            "order": index
        }
        index += 1
    if isinstance(inputs, list):
        for input_file in inputs:
            input_prefix_mapping[input_file] = {
                "prefix": "",
                "order": index,
            }
            index += 1
    elif isinstance(inputs, str):
        input_prefix_mapping[inputs] = {
            "prefix": "",
            "order": index,
        }
        inputs = [inputs]
    if gtf:
        inputs.append(gtf)
    if chromosomes:
        inputs.append(chromosomes)

    instance = Kallisto(
        tool_args=tool_args,
        inputs=inputs,
        input_prefix_mapping=input_prefix_mapping,
        output_path=output_path,
        database_name=database_name,
        database_version=database_version,
        **kwargs,
    )
    output = instance.run()
    return output


def kraken2(output_path=None, inputs=[], database_name="standard", database_version="1",
            tool_args="", read_one=None, read_two=None, remote_database_path=None, **kwargs):
    """Runs Kraken 2 via Toolchest.

    :param inputs: Path or list of paths (client-side) to be passed in as input(s).
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
    :param tool_args: (optional) Additional arguments to be passed to Kraken 2.
    :param database_name: (optional) Name of database to use for Kraken 2 alignment. Defaults to standard DB.
    :param database_version: (optional) Version of database to use for Kraken 2 alignment. Defaults to 1.
    :type database_version: str
    :param remote_database_path: (optional) Path to a custom database.
    This must be an AWS S3 URI accessible by Toolchest.
    :param read_one: (optional) Path to read 1 of paired-end read input files.
    :param read_two: (optional) Path to read 2 of paired-end read input files.

    .. note:: Paired-end read inputs can be provided either through `inputs` or
     through `read_one` and `read_two`.

     If using `inputs`, use a list of two filepaths: `inputs=['/path/to/read_1', '/path_to/read_2']`

     If using `read_one` and `read_two`, these will be interpreted as the input files
     over anything given in `inputs`.

     If using `remote_database_path`, the given database will supersede any database
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
        inputs=inputs,
        output_path=output_path,
        database_name=database_name,
        database_version=database_version,
        remote_database_path=remote_database_path,
        **kwargs,
    )
    output = instance.run()
    return output


def lastal5(output_path=None, output_primary_name="out.maf", inputs=[], database_name="standard_last",
            database_version="1", tool_args="", **kwargs):
    """Runs Last's lastal5 command via Toolchest.

    :param inputs: Path or list of paths (client-side) to be passed in as input(s).
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
    :param output_primary_name: (optional) Name of the output file.
    :param tool_args: (optional) Additional arguments to be passed to lastal5.
    :param database_name: (optional) Name of database to use for lastal5 alignment.
    :param database_version: (optional) Version of database to use for lastal5 alignment. Defaults to 1.
    :type database_version: str
    This must be an AWS S3 URI accessible by Toolchest.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.lastal5(
        ...     tool_args="",
        ...     inputs="./path/to/input.fastq",
        ...     output_path="./path/to/output",
        ... )

    """

    instance = Lastal5(
        tool_args=tool_args,
        inputs=inputs,
        output_path=output_path,
        output_primary_name=output_primary_name,
        database_name=database_name,
        database_version=database_version,
        **kwargs,
    )
    output = instance.run()
    return output


def lug(script, tool_version, custom_docker_image_id, container_name, docker_shell_location, inputs=None,
        output_path=None, tool_args="", instance_type=InstanceType.COMPUTE_2, volume_size=8, streaming_enabled=True,
        **kwargs):
    """Runs Python via Toolchest and Lug.

    :param script: path to the Python script to run.
    :param tool_version: the python version you want to use in major.minor format.
    :param custom_docker_image_id: a tagged docker image to be used as an execution environment where any calls to the
    system (via os.system(), subprocess.run(), or subprocess.Popen()) will be executed.
    :param container_name: name of docker container where lug-patched calls will be executed. Used internally.
    :param docker_shell_location: location of shell in user-specified docker container. Used internally.
    :param inputs: (optional) path(s) to the input files that will be accessible by your script at './input/'.
    :param output_path: (optional) local path to where the output file(s) will be downloaded.
    :param tool_args: (optional) additional arguments to be passed to your script as command line arguements.
    :param instance_type: (optional) allows you to select the instance that best fits the resources required for your
    script. Can accept the InstanceType enum or the underlying string (i.e. InstanceType.GENERAL_2 or "general-2").
    :param volume_size: (optional) allows you to set the amount of storage needed for your script.
    :param streaming_enabled: (optional) whether to enable live output streaming.
    usage::
        >>> import toolchest_client as toolchest
        >>> toolchest.lug(
        ...     script="./path/to/script.py",
        ...     tool_version="3.9",
        ...     custom_docker_image_id="docker-container:latest",
        ...     inputs=["./path/to/input1.txt", "./path/to/input2.fastq"],
        ...     output_path="./path/to/local/output/",
        ...     tool_args="",
        ... )
    """
    if tool_version not in ['3.7', '3.8', '3.9', '3.10', '3.11']:
        raise ToolchestException('Incompatible python version. Must be one of [3.7, 3.8, 3.9, 3.10, 3.11].')
    if inputs is None:
        inputs = []
    if type(inputs) is str:
        inputs = [inputs]
    inputs.append(script)
    tool_args = f'./input/{os.path.basename(script)};{container_name};{docker_shell_location};{tool_args}'
    instance = Lug(
        tool_args=tool_args,
        tool_version=tool_version,
        custom_docker_image_id=custom_docker_image_id,
        inputs=inputs,
        output_path=output_path,
        instance_type=instance_type,
        volume_size=volume_size,
        streaming_enabled=streaming_enabled,
        **kwargs,
    )
    output = instance.run()
    return output


def megahit(output_path=None, tool_args="", read_one=None, read_two=None, interleaved=None,
            single_end=None, **kwargs):
    """Runs Megahit via Toolchest.

    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
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
        input_prefix_mapping=input_prefix_mapping,
        inputs=input_list,
        output_path=output_path,
        **kwargs,
    )
    output = instance.run()
    return output


def metaphlan(inputs, output_path=None, output_primary_name='out.txt', tool_args="", **kwargs):
    """Runs MetaPhlAn via Toolchest.

    :param inputs: Path or list containing the path (client-side) to be passed in as input.
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
    :param output_primary_name: (optional) Name of the output file.
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
    :param tool_args: (optional) Additional arguments to be passed to MetaPhlAn.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.metaphlan(
        ...     inputs="./path/to/file.fastq",
        ...     output_path="./path/to/directory/",
        ...     output_primary_name='new_name.txt'
        ...     tool_args='',
        ... )

    """

    if "--input_type" not in tool_args:
        input_path = inputs
        if not isinstance(input_path, str):
            input_path = inputs[0]

        if 'fastq' in input_path:
            tool_args += " --input_type fastq"
        elif 'bowtie2' in input_path:
            tool_args += " --input_type bowtie2out"
        elif 'fasta' in input_path:
            tool_args += " --input_type fasta"
        elif 'sam' in input_path:
            tool_args += " --input_type sam"

    instance = MetaPhlAn(
        tool_args=tool_args,
        inputs=inputs,
        output_path=output_path,
        output_primary_name=output_primary_name,
        **kwargs,
    )
    output = instance.run()
    return output


def python3(script, inputs=None, output_path=None, tool_args="", custom_docker_image_id=None,
            instance_type=InstanceType.COMPUTE_2, volume_size=8, streaming_enabled=True, **kwargs):
    """Runs Python via Toolchest. This a restricted tool, running it requires you to request access.

    Within your Python3 script, input files are available at `./input/`.

    Only output written to `./output/` is captured by Toolchest. Writing to other directories such as
    `./temp/file.txt` is allowed. However, that file will not be captured and returned by Toolchest unless it's
    written to `./output/file.txt` instead.

    :param script: path to the Python script to run.
    :param inputs: (optional) path(s) to the input files that will be accessible by your script at './input/'.
    :param output_path: (optional) local path to where the output file(s) will be downloaded.
    :param tool_args: (optional) additional arguments to be passed to your script as command line arguements.
    :param custom_docker_image_id: (optional) a tagged docker image to be used as an execution environment that can
    provide dependencies for the script.
    :param instance_type: (optional) allows you to select the instance that best fits the resources required for your
    script. Can accept the InstanceType enum or the underlying string (i.e. InstanceType.GENERAL_2 or "general-2").
    :param volume_size: (optional) allows you to set the amount of storage needed for your script.
    :param streaming_enabled: (optional) whether to enable live output streaming.
    usage::
        >>> import toolchest_client as toolchest
        >>> toolchest.python3(
        ...     script="./path/to/script.py",
        ...     inputs=["./path/to/input1.txt", "./path/to/input2.fastq"],
        ...     output_path="./path/to/local/output/",
        ...     tool_args="",
        ... )
    """
    if inputs is None:
        inputs = []
    if type(inputs) is str:
        inputs = [inputs]
    inputs.append(script)
    tool_args = f'./input/{os.path.basename(script)} {tool_args}'
    instance = Python3(
        tool_args=tool_args,
        inputs=inputs,
        output_path=output_path,
        custom_docker_image_id=custom_docker_image_id,
        instance_type=instance_type,
        volume_size=volume_size,
        streaming_enabled=streaming_enabled,
        **kwargs,
    )
    output = instance.run()
    return output


def rapsearch2(inputs, output_path=None, output_primary_name="output", database_name="rapsearch2_seqscreen",
               database_version="1", tool_args="", **kwargs):
    """Runs RAPSearch2 via Toolchest.
    :param inputs: Path to a FASTA/FASTQ file that will be passed in as input.
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
    :param output_primary_name: (optional) Base name of output file(s).
    (Functions the same way as the "-o" tag for RAPSearch2, in combination with `output_path`.)
    :param tool_args: (optional) Additional arguments to be passed to RAPSearch2.
    :param database_name: (optional) Name of database to use for RAPSearch2 alignment. Defaults to SeqScreen DB.
    :param database_version: (optional) Version of database to use for RAPSearch2 alignment. Defaults to 1.
    :type database_version: str
    Usage::
        >>> import toolchest_client as toolchest
        >>> toolchest.rapsearch(
        ...     tool_args="",
        ...     inputs="./path/to/input",
        ...     output_path="./path/to/output/",
        ...     output_primary_name="base"
        ...     # full base output path (-o flag) is ./path/to/output/base
        ... )
    """

    instance = Rapsearch2(
        tool_args=tool_args,
        database_name=database_name,
        database_version=database_version,
        inputs=inputs,
        output_path=output_path,
        output_primary_name=output_primary_name,
        **kwargs,
    )
    output = instance.run()
    return output


# Adds rapsearch as an alias for rapsearch2
rapsearch = rapsearch2


def salmon(output_path=None, tool_args="", read_one=None, read_two=None, single_end=None, library_type="A",
           database_name="salmon_hg38", database_version="1", **kwargs):
    """Runs Salmon via Toolchest.

    :param database_name: Name of database to use for STAR alignment (defaults to GRCh38).
    :param database_version: Version of database to use for STAR alignment (defaults to 1).
    :param library_type: (optional) `--libType` value. Defaults to "A" for automatic. See
    https://salmon.readthedocs.io/en/latest/salmon.html#what-s-this-libtype
    :param output_path: (optional) Path (local or S3) to a directory where the output files will be downloaded.
    :param read_one: (optional) `-1` inputs. Path or list of paths for read 1 of paired-read input files.
    :param read_two: (optional) `-2` inputs. Path or list of paths for read 2 of paired-read input files.
    :param single_end: (optional) `-r` inputs. Path or list of paths for single-end inputs (no interleaved files).
    :param tool_args: (optional) Additional arguments to be passed to Salmon.

    .. note:: Each read in `read_one` should match with a read in `read_two`, and vice
    versa. In other words, the nth read in `read_one` should be paired with the nth read
    in `read_two`.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.salmon(
        ...     tool_args="",
        ...     read_one=["./pair_1/r1.fa", "./pair_2/r1.fa"],
        ...     read_two=["./pair_1/r2.fa", "./pair_2/r2.fa"],
        ...     output_path="./path/to/output",
        ... )

    """

    # Guard against library type in tool args
    if "-l" in tool_args or "--libType" in tool_args:
        raise ValueError("A library type is set in 'tool_args'. Use the 'library_type' argument instead.")

    # If input parameters are lists, parse these for input_prefix_mapping.
    tag_to_param_map = {
        "-1": read_one,
        "-2": read_two,
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

    instance = Salmon(
        database_name=database_name,
        database_version=database_version,
        input_prefix_mapping=input_prefix_mapping,
        inputs=input_list,
        output_path=output_path,
        tool_args=f"--libType {library_type} {tool_args}",
        **kwargs,
    )
    output = instance.run()
    return output


def shi7(inputs, output_path=None, tool_args="", **kwargs):
    """Runs shi7 via Toolchest.

    :param tool_args: (optional) Additional arguments to be passed to shi7.
    :param inputs: Path or list of paths (client-side) to be passed in as input.
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
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
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
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
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
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
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.
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
        output_primary_name="Aligned.out.sam" if parallelize else None,
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
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.test(
        ...     inputs="./path/to/input.txt",
        ...     output_path="./path/to/output.txt",
        ... )

    """

    instance = Test(
        tool_args=tool_args,
        inputs=inputs,
        output_path=output_path,
        **kwargs,
    )
    output = instance.run()
    return output


def transfer(inputs, output_path=None, **kwargs):
    """Transfers files via Toolchest from an input (local, S3, or HTTP) to an output directory (local or S3)."

    :param inputs: Path or list of files (local, S3, or HTTP) to be transferred.
    :param output_path: Path (local or S3) to a directory where the output files will be downloaded.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.transfer(
        ...     inputs=[
        ...       "https://rest.uniprot.org/uniprotkb/P48754.fasta",
        ...       "https://rest.uniprot.org/uniprotkb/P48755.fasta",
        ...     ],
        ...     output_path="s3://example/uniprot/",
        ... )

    """
    if 'instance_type' in kwargs:
        raise ToolchestException("Argument 'instance_type' is not supported by transfer currently.")

    if isinstance(inputs, list):
        if not path_is_s3_uri(output_path):
            raise NotImplementedError("Transferring multiple files at once is supported only for an S3 output_path")

    instance = Transfer(
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
    :param output_path: (optional) Path (client-side) to a directory where the output files will be downloaded.

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


def update_database(database_path, tool, database_name, database_primary_name=None, is_async=True, **kwargs):
    """Updates a custom database. The new database version is returned immediately after initialization.

    This executes just like any other tool, except:
    - the success status is
    toolchest_client.api.status.COMPLETE ('complete') instead of
    toolchest_client.api.status.READY_TO_TRANSFER_TO_CLIENT ('ready_to_transfer_to_client')
    - is_async is True by default (but can be set to False)

    Note that it may take at least a few minutes for the custom database to be ready for use.
    Larger databases will require more time (roughly 1 extra minute for every 5-10 GB).
    To ensure that subsequent Toolchest calls will be run after the database is ready to use,
    set `is_async=False`.

    If there are multiple files being uploaded, Toolchest will assume that a directory containing
    all database files should be passed in as the database for the tool on the command line. If
    only one of these files should be specified instead, use the `database_primary_name` argument
    to specify this file.

    :param database_path: Path or list of paths (local or S3) to be passed in as inputs.
    :param tool: Toolchest tool with which you use the database (e.g. toolchest.tools.Kraken2).
    :param database_name: Name of database to update.
    :param database_primary_name: Base name of the file/prefix that would normally be passed in
        to the command line call. If left unspecified, assumes the primary name of the previous
        version.
    :param is_async: Whether to run the database addition asynchronously. Unlike tool runs,
        this is set to `True` by default.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.update_database(
        ...     database_path="s3://toolchest-public-examples-no-encryption/integration-test-db/bowtie2-fruitfly",
        ...     tool=toolchest.tools.Bowtie2,
        ...     database_name="my_new_database",
        ...     database_primary_name="Dmel_A4_1.0",
        ... )

    """

    instance = tool(
        inputs=database_path,
        database_name=database_name,
        is_async=is_async,
        is_database_update=True,
        database_primary_name=database_primary_name,
        output_path=None,
        output_primary_name=None,
        database_version=None,
        tool_args="",
        remote_database_path=None,
        max_inputs=1000,
        volume_size=8,
        instance_type=InstanceType.COMPUTE_2,
        # Only compress inputs if a single local directory/file is given.
        # (Tool._prepare_inputs() will skip compressing single S3/HTTP inputs,
        # and lists of local files will not be compressed.)
        compress_inputs=True if isinstance(database_path, str) else False,
        **kwargs,
    )
    output = instance.run()
    return output


def add_database(database_path, tool, database_name, database_primary_name, is_async=True, **kwargs):
    """Adds a custom database and attaches it to a tool.
    The new database version is returned immediately after initialization.

    This executes just like any other tool, except:
    - the success status is
    toolchest_client.api.status.COMPLETE ('complete') instead of
    toolchest_client.api.status.READY_TO_TRANSFER_TO_CLIENT ('ready_to_transfer_to_client')
    - is_async is True by default (but can be set to False)

    Note that it may take at least a few minutes for the custom database to be ready for use.
    Larger databases will require more time (roughly 1 extra minute for every 5-10 GB).
    To ensure that subsequent Toolchest calls will be run after the database is ready to use,
    set `is_async=False`.

    If there are multiple files being uploaded, Toolchest will assume that a directory containing
    all database files should be passed in as the database for the tool on the command line. If
    only one of these files should be specified instead, use the `database_primary_name` argument
    to specify this file.

    :param database_path: Path or list of paths (local or S3) to be passed in as inputs.
    :param tool: Toolchest tool with which you use the database (e.g. toolchest.tools.Kraken2).
    :param database_name: Name of the new database.
    :param database_primary_name: Base name of the file/prefix that would normally be passed in
        to the command line call. Use `database_primary_name=None` to use the directory name
        as the database.
    :param is_async: Whether to run the database addition asynchronously. Unlike tool runs,
        this is set to `True` by default.

    Usage::

        >>> import toolchest_client as toolchest
        >>> toolchest.add_database(
        ...     database_path="s3://toolchest-public-examples-no-encryption/integration-test-db/bowtie2-fruitfly",
        ...     tool=toolchest.tools.Bowtie2,
        ...     database_name="my_new_database",
        ...     database_primary_name="Dmel_A4_1.0",
        ... )

    """

    instance = tool(
        inputs=database_path,
        database_name=database_name,
        is_async=is_async,
        is_database_update=True,
        database_primary_name=database_primary_name,
        output_path=None,
        output_primary_name=None,
        database_version=None,
        tool_args="",
        remote_database_path=None,
        max_inputs=1000,
        volume_size=8,
        instance_type=InstanceType.COMPUTE_2,
        # Only compress inputs if a single local directory/file is given.
        # (Tool._prepare_inputs() will skip compressing single S3/HTTP inputs,
        # and lists of local files will not be compressed.)
        compress_inputs=True if isinstance(database_path, str) else False,
        **kwargs,
    )
    output = instance.run()
    return output

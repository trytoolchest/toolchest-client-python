"""
toolchest_client.files.merge
~~~~~~~~~~~~~~~~~~~~~~

Functions for merging files
"""

import multiprocessing
import shutil


def concatenate_files(input_file_paths, output_file_path):
    """Concatenates a list of files using shutil.

    :param input_file_paths: Paths to the files which are to be concatenated.
    :param output_file_path: Path to the merged output file.
    """
    with open(output_file_path, "wb") as output_file:
        for input_file_path in input_file_paths:
            input_file = open(input_file_path, "rb")
            shutil.copyfileobj(input_file, output_file)
            input_file.close()


def merge_sam_files(input_file_paths, output_file_path):
    """Merges SAM files – the output for tools like STAR – using samtools.

    :param input_file_paths: Paths to the files which are to be merged with samtools.
    :param output_file_path: Path to the merged output file.
    """
    # Only import pysam – an optional dependency – if absolutely needed
    import pysam

    # This cause problems if run on a shared machine with non-available cores
    num_cores = multiprocessing.cpu_count()

    # Options for merging SAM files:
    # -f: force overwrite output file
    # -o: specify output manually
    # -u: write output as an uncompressed SAM
    # -c: combine headers when they exist in both files
    # -p: merge @PG IDs
    # --threads: number of threads
    # todo: verify that this works correctly with real output files
    pysam.merge(
        "-f",
        "-u",
        "-c",
        "-p",
        "--threads",
        f"{num_cores}",
        output_file_path,
        *input_file_paths
    )

"""
toolchest_client.files
~~~~~~~~~~~~~~~~~~~~~~

This file provides an interface to handle files and their errors.
"""
import multiprocessing
import os
import pathlib
import pysam
import shutil


def assert_exists(path, must_be_file=False):
    """Raises an error if a path does not exist.
    Optionally, confirms that a path is to a file.

    :param path: A path.
    :type path: string
    :param must_be_file: Whether the path must be to a file.
    :type must_be_file: bool
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No file or directory found at {path}")
    if must_be_file and not os.path.isfile(path):
        raise ValueError(f"Directory entry at {path} is not a file")


def check_file_size(file_path, max_size_bytes=None):
    """Raises an error if the file is above the non-multipart upload limit for S3 (5GB)

    :param file_path: A path to a file.
    :type file_path: string
    :param max_size_bytes: Maximum number of bytes allowed for a file. Throws error if above limit.
    :type max_size_bytes: int | None
    """
    assert_exists(file_path, must_be_file=True)
    file_size_bytes = os.stat(file_path).st_size
    if max_size_bytes:
        if file_size_bytes >= max_size_bytes:
            raise ValueError(f"File at {file_path} is larger than your plan's per-file limit")
    return file_size_bytes


def files_in_path(files):
    """Returns a list of all files found within the provided input path(s).

    :param files: A string or list of strings to files and directories.
    :type files: string | list
    """
    # If it's a list, find all the files within all of the elements
    if isinstance(files, list):
        more_files = []
        for sub_path in files:
            more_files.extend(files_in_path(sub_path))
        return more_files

    # If it's a path to something that doesn't exist, error
    assert_exists(files, must_be_file=False)

    # If it's a path is to a single file, return a list containing just the path to that file
    if os.path.isfile(files):
        return [files]

    # If it's a directory, return a list of paths to all files in the directory
    files_and_directories = os.listdir(files)
    more_files = []
    for sub_path in files_and_directories:
        abs_sub_path = os.path.join(files, sub_path)
        more_files.extend(files_in_path(abs_sub_path))

    return more_files


# todo: better define working directory location
def open_new_output_file(
        current_split_number,
        input_basename,
        working_directory="./temp_toolchest",
        filename_prefix="input_split"
):
    """Opens a new file for parallelization.

    :param current_split_number: The current segment of the parallelization.
    :param input_basename: The name of the file without the path (e.g. test.fasta).
    :param working_directory: Where to write the new output files.
    :param filename_prefix: Prefix to identify the splits.
    """
    if not os.path.exists(working_directory):
        os.mkdir(working_directory)
    current_output_file_path = f"{working_directory}/{filename_prefix}_{current_split_number}_{input_basename}"
    return current_output_file_path, open(current_output_file_path, "w")


def split_file_by_lines(input_file_path, num_lines_in_group=4, max_bytes=5 * 1024 * 1024 * 1024):
    """Splits files by line. Defaults to splitting files by four line groups to support
    FASTA and FASTQ files. Note that this is a generator.

    :param input_file_path: Path to the file which is to be split.
    :param num_lines_in_group: Number of contiguous lines which cannot be split from one another.
    :param max_bytes: Maximum size of each new file.
    """
    file_extension = pathlib.Path(input_file_path).suffix
    if file_extension not in [".fastq", ".fasta", ".fa", ".fq", ".fna"]:
        raise ValueError("Cannot split a non FASTQ/FASTA file for parallelization")

    input_basename = os.path.basename(input_file_path)
    current_split_number = 0
    current_output_bytes = 0
    current_line_number = 0
    current_output_file_path, current_output_file = open_new_output_file(
        current_split_number=current_split_number,
        input_basename=input_basename
    )
    large_input_file = open(input_file_path, "r")

    for line in large_input_file:
        current_line_number += 1
        # Assume that each character is one byte (inaccurate, but good enough for our use case)
        bytes_in_line = len(line)
        current_output_bytes += bytes_in_line
        if current_output_bytes >= max_bytes and current_line_number % num_lines_in_group == 0:
            # Time to switch output files
            current_output_bytes = 0
            current_output_file.close()
            yield current_output_file_path
            current_split_number += 1
            current_output_file_path, current_output_file = open_new_output_file(
                current_split_number=current_split_number,
                input_basename=input_basename
            )
        else:
            # Not time to switch output files yet
            current_output_file.write(f"{line}")

    current_output_file.close()
    large_input_file.close()
    yield current_output_file_path


def sanity_check(file_path):
    """Ensures file is greater than an arbitrary small size (5 bytes).

    :param file_path: Path to the file which is to be checked.
    """
    assert_exists(file_path, must_be_file=True)
    if os.stat(file_path).st_size <= 5:
        raise ValueError(f"File at {file_path} is suspiciously small")


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

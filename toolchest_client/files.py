"""
toolchest_client.files
~~~~~~~~~~~~~~~~~~~~~~

This file provides an interface to handle files and their errors.
"""
import os
import pathlib
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


def check_file_size(file_path):
    """Raises an error if the file is above the non-multipart upload limit for S3 (5GB)

    :param file_path: A path to a file.
    :type file_path: string
    """
    assert_exists(file_path, must_be_file=True)
    if os.stat(file_path).st_size >= 5 * 1024 * 1024 * 1024:
        raise ValueError(f"File at {file_path} is larger than your plan's per-file 5GB limit")


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
        check_file_size(files)
        return [files]

    # If it's a directory, return a list of paths to all files in the directory
    files_and_directories = os.listdir(files)
    more_files = []
    for sub_path in files_and_directories:
        abs_sub_path = os.path.join(files, sub_path)
        more_files.extend(files_in_path(abs_sub_path))

    return more_files


# todo: better define working directory location
def open_new_output_file(current_split_number, input_basename, working_directory="./temp_toolchest", filename_prefix="input_split"):
    if not os.path.exists(working_directory):
        os.mkdir(working_directory)
    current_output_file_path = f"{working_directory}/{filename_prefix}_{current_split_number}_{input_basename}"
    return current_output_file_path, open(current_output_file_path, "w")


# default line split of 4 to handle FASTQ and FASTA files
def split_file_by_lines(input_file_path, num_lines_in_group=4, max_bytes=5 * 1024 * 1024 * 1024):
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
    split_input_files = [current_output_file_path]
    large_input_file = open(input_file_path, "r")

    for line in large_input_file:
        current_line_number += 1
        # assume that each character is one byte (a bad assumption, but good enough for our use case)
        bytes_in_line = len(line)
        current_output_bytes += bytes_in_line
        if current_output_bytes >= max_bytes and current_line_number % num_lines_in_group == 0:
            # Time to switch output files
            current_output_bytes = 0
            current_output_file.close()
            current_split_number += 1
            current_output_file_path, current_output_file = open_new_output_file(
                current_split_number=current_split_number,
                input_basename=input_basename
            )
            split_input_files.append(current_output_file_path)
        else:
            # Not time to switch output files yet
            current_output_file.write(f"{line}")

    current_output_file.close()
    large_input_file.close()
    return split_input_files


def sanity_check(file_path):
    # Assert file exists and is non-zero
    assert_exists(file_path, must_be_file=True)
    if os.stat(file_path).st_size <= 10:
        raise ValueError(f"File at {file_path} is suspiciously small")


def concatenate_files(input_file_paths, output_file_path):
    with open(output_file_path, "wb") as output_file:
        for input_file_path in input_file_paths:
            input_file = open(input_file_path, "rb")
            shutil.copyfileobj(input_file, output_file)
            input_file.close()

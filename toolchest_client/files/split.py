import os
import pathlib

"""
toolchest_client.files.split
~~~~~~~~~~~~~~~~~~~~~~

Functions for splitting files
"""


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
    return current_output_file_path, open(current_output_file_path, "w", newline="\n")


def split_file_by_lines(input_file_path, num_lines_in_group=4, max_bytes=4.5 * 1024 * 1024 * 1024):
    """Splits files by line. Defaults to splitting files by four line groups to support
    FASTA and FASTQ files. Note that this is a generator.

    :param input_file_path: Path to the file which is to be split.
    :param num_lines_in_group: Number of contiguous lines which cannot be split from one another.
    :param max_bytes: Maximum size of each new file.
    """
    print(f"Creating file splits for {input_file_path}...")
    file_extension = pathlib.Path(input_file_path).suffix
    if file_extension not in [".fastq", ".fasta", ".fa", ".fq", ".fna"]:
        raise ValueError("Cannot split a non FASTQ/FASTA file for parallelization")

    input_basename = os.path.basename(input_file_path)
    current_split_number = 0
    current_output_bytes = 0
    current_line_number = 0
    need_to_open_new_file = True
    current_output_file_path = ''
    current_output_file = None
    large_input_file = open(input_file_path, "r")

    for line in large_input_file:
        if need_to_open_new_file:
            current_output_file_path, current_output_file = open_new_output_file(
                current_split_number=current_split_number,
                input_basename=input_basename
            )
            need_to_open_new_file = False

        current_line_number += 1
        # Assume that each character is one byte (inaccurate, but good enough for our use case)
        bytes_in_line = len(line)
        current_output_bytes += bytes_in_line
        current_output_file.write(f"{line}")
        if current_output_bytes >= max_bytes and current_line_number % num_lines_in_group == 0:
            # Time to switch output files
            current_output_bytes = 0
            current_output_file.close()
            yield current_output_file_path
            current_split_number += 1
            need_to_open_new_file = True

    current_output_file.close()
    large_input_file.close()
    if current_output_bytes != 0:
        yield current_output_file_path

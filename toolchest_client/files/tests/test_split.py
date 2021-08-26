import filecmp
import os
import pathlib

from .. import split_file_by_lines

THIS_FILE_PATH = pathlib.Path(__file__).parent.resolve()


def delete_temp_files(file_paths):
    """
    Deletes temporary files. Only use for testing.
    """
    for file_path in file_paths:
        os.remove(file_path)


def assert_files_eq(file_path_one, file_path_two):
    assert filecmp.cmp(file_path_one, file_path_two)


def test_split_small_fastq():
    new_file_paths = []
    split_file_paths = split_file_by_lines(
        input_file_path=f"{THIS_FILE_PATH}/data/eight_line.fastq",
        num_lines_in_group=4,
        max_bytes=100
    )

    for file_path in split_file_paths:
        new_file_paths.append(file_path)

    assert len(new_file_paths) == 2

    assert_files_eq(new_file_paths[0], f"{THIS_FILE_PATH}/data/eight_line_split_one.fastq")
    assert_files_eq(new_file_paths[1], f"{THIS_FILE_PATH}/data/eight_line_split_two.fastq")

    delete_temp_files(new_file_paths)


def test_split_small_fastq_small_bytes():
    new_file_paths = []
    split_file_paths = split_file_by_lines(
        input_file_path=f"{THIS_FILE_PATH}/data/eight_line.fastq",
        num_lines_in_group=4,
        max_bytes=1
    )

    for file_path in split_file_paths:
        new_file_paths.append(file_path)

    assert len(new_file_paths) == 2

    assert_files_eq(new_file_paths[0], f"{THIS_FILE_PATH}/data/eight_line_split_one.fastq")
    assert_files_eq(new_file_paths[1], f"{THIS_FILE_PATH}/data/eight_line_split_two.fastq")

    delete_temp_files(new_file_paths)

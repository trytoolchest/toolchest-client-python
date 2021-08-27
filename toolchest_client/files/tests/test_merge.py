import filecmp
import os
import pathlib

import pytest

from .. import concatenate_files, merge_sam_files

THIS_FILE_PATH = pathlib.Path(__file__).parent.resolve()


def test_concatenate_files():
    input_file_path = f"{THIS_FILE_PATH}/data/eight_line.fastq"
    split_one_path = f"{THIS_FILE_PATH}/data/eight_line_split_one.fastq"
    split_two_path = f"{THIS_FILE_PATH}/data/eight_line_split_two.fastq"
    temp_output_file_path = f"{THIS_FILE_PATH}/data/temp_output.fastq"

    concatenate_files([split_one_path, split_two_path], temp_output_file_path)

    assert filecmp.cmp(input_file_path, temp_output_file_path)

    os.remove(temp_output_file_path)

# TODO: test merge_sam_files() in a way that's reproducible on different OS choices

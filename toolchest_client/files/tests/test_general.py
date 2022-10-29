import os
import pathlib

import pytest

from .. import assert_exists, check_file_size, files_in_path, sanity_check, convert_input_params_to_prefix_mapping

THIS_FILE_PATH = os.path.normpath(pathlib.Path(__file__).parent.resolve())


def test_small_file():
    small_file_path = f"{THIS_FILE_PATH}/data/very_small_file.txt"
    with pytest.raises(ValueError):
        sanity_check(small_file_path)


def test_files_in_path():
    tmp_dir = f"{THIS_FILE_PATH}/tmp"
    tmp1 = f"{tmp_dir}/tmp1"
    tmp2 = f"{tmp_dir}/tmp2"
    sub_dir = f"{tmp_dir}/sub_dir"
    tmp3 = f"{sub_dir}/tmp3"
    file_paths = [tmp1, tmp2, tmp3]
    os.makedirs(sub_dir, exist_ok=True)
    for file in file_paths:
        open(file, "w").close()
    file_paths = sorted([os.path.normpath(x) for x in file_paths])

    assert sorted([os.path.normpath(x) for x in files_in_path(tmp_dir)]) == file_paths

    for file in file_paths:
        os.remove(file)
    os.removedirs(sub_dir)


def test_file_too_large():
    with pytest.raises(ValueError):
        check_file_size(f"{THIS_FILE_PATH}/data/eight_line.fastq", max_size_bytes=100)


def test_nonexistent_file():
    bogus_file_path = f"{THIS_FILE_PATH}/data/bogus_file_path"
    with pytest.raises(FileNotFoundError):
        assert_exists(bogus_file_path)


def test_exists_but_not_file():
    dir_file_path = f"{THIS_FILE_PATH}/data"
    with pytest.raises(ValueError):
        assert_exists(dir_file_path, must_be_file=True)


def test_generate_prefix_mapping():
    tag_to_param_map = {
        "-1": ["example1_R1.fastq", "example2_R1.fastq"],
        "-2": ["example1_R2.fastq", "example2_R2.fastq"],
        "-U": ["example1_U.fastq", "example2_U.fastq"],
    }
    input_list, prefix_mapping = convert_input_params_to_prefix_mapping(tag_to_param_map)
    assert sorted(input_list) == sorted([
        "example1_R1.fastq",
        "example2_R1.fastq",
        "example1_R2.fastq",
        "example2_R2.fastq",
        "example1_U.fastq",
        "example2_U.fastq",
    ])
    assert prefix_mapping == {
        "example1_R1.fastq": {
            "prefix": "-1",
            "order": 0,
        },
        "example1_R2.fastq": {
            "prefix": "-2",
            "order": 0,
        },
        "example1_U.fastq": {
            "prefix": "-U",
            "order": 0,
        },
        "example2_R1.fastq": {
            "prefix": "-1",
            "order": 1,
        },
        "example2_R2.fastq": {
            "prefix": "-2",
            "order": 1,
        },
        "example2_U.fastq": {
            "prefix": "-U",
            "order": 1,
        },
    }

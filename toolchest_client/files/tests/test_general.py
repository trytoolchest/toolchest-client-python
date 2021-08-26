import filecmp
import os
import pathlib

import pytest

from .. import assert_exists, check_file_size, files_in_path, sanity_check

THIS_FILE_PATH = pathlib.Path(__file__).parent.resolve()


def test_small_file():
    small_file_path = f"{THIS_FILE_PATH}/data/very_small_file.txt"
    with pytest.raises(ValueError):
        sanity_check(small_file_path)

def test_files_in_path():
    pass

def test_file_too_large():
    pass

def test_nonexistent_file():
    bogus_file_path = f"{THIS_FILE_PATH}/data/bogus_file_path"
    with pytest.raises(FileNotFoundError):
        assert_exists(bogus_file_path)

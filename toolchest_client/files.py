"""
toolchest_client.files
~~~~~~~~~~~~~~~~~~~~~~

This file provides an interface to handle files and their errors.
"""
import os

# Determine if a path is a file


def assert_exists(path, must_be_file=False):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No file or directory found at {path}")
    if must_be_file and not os.path.isfile(path):
        raise ValueError(f"Directory entry at {path} is not a file")


# Non-multipart uploads to S3 are limited at 5GB
def check_file_size(file_path):
    assert_exists(file_path, must_be_file=True)
    if os.stat(file_path).st_size >= 5 * 1024 * 1024 * 1024:
        raise ValueError(f"File at {file_path} is larger than your plan's per-file 5GB limit")


# Takes in a path to a file or directory
# Returns a list paths to files
def files_in_path(path):
    # If path doesn't exist, error
    assert_exists(path, must_be_file=False)

    # If path is to a file, return the file
    if os.path.isfile(path):
        check_file_size(path)
        return [path]

    # If path is to a directory, return all files within the directory
    files_and_directories = os.listdir(path)
    files = []
    for sub_path in files_and_directories:
        abs_sub_path = os.path.join(path, sub_path)
        files.extend(files_in_path(abs_sub_path))

    return files

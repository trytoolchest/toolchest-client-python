"""
toolchest_client.files
~~~~~~~~~~~~~~~~~~~~~~

This file provides an interface to handle files and their errors.
"""
import os


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

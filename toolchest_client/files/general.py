"""
toolchest_client.files.general
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

General file handling functions.
"""

import os
import shutil

from .public_uris import get_url_with_protocol, path_is_http_url, path_is_accessible_ftp_url, \
    get_ftp_url_file_size
from .s3 import assert_accessible_s3, get_s3_file_size, path_is_s3_uri


def assert_exists(path, must_be_file=False, must_be_directory=False):
    """Raises an error if a path does not exist.
    Optionally, confirms that a path is to a file.

    :param path: A path.
    :type path: string
    :param must_be_file: Whether the path must be to a file.
    :type must_be_file: bool
    :param must_be_directory: Whether the path must be to a directory.
    :type must_be_directory: bool
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No accessible file or directory found at {path}")
    if must_be_file and not os.path.isfile(path):
        raise ValueError(f"Directory entry at {path} is not a file")
    if must_be_directory and not os.path.isdir(path):
        raise ValueError(f"Directory entry at {path} is not a directory")


def check_file_size(file_path, max_size_bytes=None):
    """Raises an error if the file is above the non-multipart upload limit for S3 (5GB)

    :param file_path: A path to a file.
    :type file_path: string
    :param max_size_bytes: Maximum number of bytes allowed for a file. Throws error if above limit.
    :type max_size_bytes: int | None
    """
    if path_is_s3_uri(file_path):
        # Get file size S3 metadata, via API.
        # NOTE: If the file is already in S3, the size is checked as well to enforce an expected file size
        file_size_bytes = get_s3_file_size(file_path)
    elif path_is_http_url(file_path):
        # Client does not track size for http inputs
        file_size_bytes = 0
    elif path_is_accessible_ftp_url(file_path):
        # Get file size via a SIZE request
        file_size_bytes = get_ftp_url_file_size(file_path)
    else:
        assert_exists(file_path, must_be_file=True)
        file_size_bytes = os.stat(file_path).st_size

    if max_size_bytes:
        if file_size_bytes >= max_size_bytes:
            raise ValueError(f"File at {file_path} is larger than your per-file limit for this tool")

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

    # If it's an S3 URI, treat it as a file
    # Check if it is accessible from a worker node
    if path_is_s3_uri(files):
        assert_accessible_s3(files)
        return [files]

    # If it's an HTTP or HTTPS URL, treat it as a file
    if path_is_http_url(files):
        return [get_url_with_protocol(files)]

    # If it's an FTP URL, treat it as a file
    if path_is_accessible_ftp_url(files):
        return [files]

    # Path is local, expand ~ in path if present
    files = os.path.expanduser(files)

    # If it's a path to something that doesn't exist, error
    assert_exists(files, must_be_file=False)

    # If it's a path to a single file, return a list containing just the path to that file
    if os.path.isfile(files):
        return [files]

    # If it's a directory, return a list of paths to all files in the directory
    files_and_directories = os.listdir(files)
    more_files = []
    for sub_path in files_and_directories:
        abs_sub_path = os.path.join(files, sub_path)
        more_files.extend(files_in_path(abs_sub_path))

    return more_files


def compress_files_in_path(file_path):
    """Returns a tarred and compressed file containing the contents of a directory.

    WARNING: this is NOT thread-safe, as shutil.make_archive is not thread safe.

    :param file_path: A string to a local directory.
    """
    assert_exists(file_path)
    temp_directory = os.environ.get("TOOLCHEST_TEMP_DIR") or "./temp_toolchest"

    print(f"Creating an archive of all files in {file_path}...")
    zip_location = shutil.make_archive(
        base_name=f"{temp_directory}/{os.path.basename(file_path)}",
        format="gztar",
        root_dir=os.path.dirname(file_path),
        base_dir=os.path.basename(file_path)
    )

    return zip_location


def sanity_check(file_path):
    """Ensures file is greater than an arbitrary small size (5 bytes).

    :param file_path: Path to the file which is to be checked.
    """
    assert_exists(file_path, must_be_file=True)
    if os.stat(file_path).st_size <= 5:
        raise ValueError(f"File at {file_path} is suspiciously small")


def convert_input_params_to_prefix_mapping(tag_to_param_map):
    """
    Parses input parameters in a Toolchest call into:
    - a list of all input paths (for uploading)
    - a mapping of inputs to their respective prefixes

    Example input params map:
    {
        "-1": ["example_R1.fastq"],
        "-2": ["example_R2.fastq"],
        "-U": ["example_U.fastq"],
    }

    Example output list:
    [example_R1.fastq, example_R2.fastq, example_U.fastq]

    Example output prefix mapping:
    {
        "example_R1.fastq": {
            "prefix": "-1",
            "order": 0,
        },
        "example_R2.fastq": {
            "prefix": "-2",
            "order": 0,
        },
        "example_U.fastq": {
            "prefix": "-U",
            "order": 0,
        },
    }
    """
    input_list = []  # list of all inputs
    input_prefix_mapping = {}  # map of each input to its respective tag
    for tag, param in tag_to_param_map.items():
        if isinstance(param, list):
            for index, input_file in enumerate(param):
                input_list.append(input_file)
                input_prefix_mapping[input_file] = {
                    "prefix": tag,
                    "order": index,
                }
        elif isinstance(param, str):
            input_list.append(param)
            input_prefix_mapping[param] = {
                "prefix": tag,
                "order": 0,
            }
    return input_list, input_prefix_mapping

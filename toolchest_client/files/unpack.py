from enum import Enum
import os
import shutil
import tarfile


class OutputType(Enum):
    GZ_TAR = ".tar.gz"
    FLAT_TEXT = ".txt"
    SAM_FILE = ".sam"


def unpack_files(file_path_to_unpack, output_type):
    """Unpack output file, if needed. Returns the path(s) to the (optionally) unpacked output.
    If only 1 file is unpacked, returns a string containing that file's path.
    If there are multiple unpacked files, returns a list of paths.
    """
    if output_type == OutputType.FLAT_TEXT:
        return file_path_to_unpack
    elif output_type == OutputType.SAM_FILE:
        return file_path_to_unpack
    elif output_type == OutputType.GZ_TAR:
        # Get names of files in archive
        with tarfile.open(file_path_to_unpack) as tar:
            unpacked_file_names = tar.getnames()

        unpacked_outputs_dir = os.path.dirname(file_path_to_unpack)
        shutil.unpack_archive(
            filename=file_path_to_unpack,
            extract_dir=unpacked_outputs_dir,
            format="gztar",
        )

        # Remove the unpacked .tar.gz file and empty unpacked output folder
        os.remove(file_path_to_unpack)

        unpacked_paths = ["/".join([unpacked_outputs_dir, file_name]) for file_name in unpacked_file_names]
        unpacked_file_paths = [os.path.normpath(path) for path in unpacked_paths if os.path.isfile(path)]

        # If only 1 file is unpacked, just return path instead of [path].
        # This is to be consistent with the return value from the other output types.
        if len(unpacked_file_paths) == 1:
            return unpacked_file_paths[0]
        return unpacked_file_paths

    else:
        raise NotImplementedError(f"Output type {output_type} unpacking is not implemented")


def get_file_type(file_path):
    """Gets file type from available types registered in OutputType.
    Raises an error if the file does not match any registered type.

    TODO: add default handling for plaintext files apart from .txt files
    """
    for output_type in OutputType:
        if file_path.endswith(output_type.value):
            return output_type
    raise NotImplementedError(f"Handling of output type for file at {file_path} is not implemented")

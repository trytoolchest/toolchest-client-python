from enum import Enum
import os
import shutil
import tarfile


class OutputType(Enum):
    GZ_TAR = ".tar.gz"
    FLAT_TEXT = ".txt"
    SAM_FILE = ".sam"
    S3 = ""


def unpack_files(file_path_to_unpack, is_compressed):
    """Unpack output file, if needed. Returns the path(s) to the (optionally) unpacked output.
    Returns a list of file paths to unpacked files.
    """
    if is_compressed:
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

        return unpacked_file_paths
    else:
        return file_path_to_unpack

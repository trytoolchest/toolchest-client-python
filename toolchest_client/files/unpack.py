from enum import Enum
import os
import shutil


class OutputType(Enum):
    GZ_TAR = ".tar.gz"
    FLAT_TEXT = ".txt"
    SAM_FILE = ".sam"


def unpack_files(file_path_to_unpack, output_type):
    """Unpack output file, if needed. Returns the path to the (optionally) unpacked output."""
    if output_type == OutputType.FLAT_TEXT:
        return file_path_to_unpack
    elif output_type == OutputType.SAM_FILE:
        return file_path_to_unpack
    elif output_type == OutputType.GZ_TAR:
        unpacked_outputs_dir = os.path.dirname(file_path_to_unpack)
        shutil.unpack_archive(
            filename=file_path_to_unpack,
            extract_dir=unpacked_outputs_dir,
            format="gztar",
        )

        # Remove the unpacked .tar.gz file and empty unpacked output folder
        os.remove(file_path_to_unpack)
    else:
        raise NotImplementedError(f"Output type {output_type} unpacking is not implemented")

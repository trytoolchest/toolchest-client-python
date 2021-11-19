from distutils.dir_util import copy_tree
from enum import Enum
import os
import shutil


class OutputType(Enum):
    GZ_TAR = ".tar.gz"
    FLAT_TEXT = ".txt"


def unpack_files(file_path_to_unpack, output_type):
    """Unpack output file, if needed. Returns the path to the (optionally) unpacked output."""
    if output_type == OutputType.FLAT_TEXT:
        # Flat text needs no post-processing
        return file_path_to_unpack
    elif output_type == OutputType.GZ_TAR:
        # TODO: better validate the output of the unpacked files
        # The underlying shutil code does some, but it's limited
        unpacked_outputs_final_destination = os.path.dirname(file_path_to_unpack)
        shutil.unpack_archive(
            filename=file_path_to_unpack,
            extract_dir=unpacked_outputs_final_destination,
            format="gztar",
        )

        # Assumes the resulting unpacked archive is named "output", which is true by spec
        unpacked_outputs_intermediate_dir = f"{unpacked_outputs_final_destination}/output"
        files_moved = copy_tree(
            src=unpacked_outputs_intermediate_dir,
            dst=unpacked_outputs_final_destination,
            preserve_symlinks=True,
        )
        if len(files_moved) == 0:
            raise ValueError(
                f"No files exist within {unpacked_outputs_intermediate_dir}, no files to unpack"
            )

        # Remove the unpacked .tar.gz file and empty unpacked output folder
        os.remove(file_path_to_unpack)
        # Ensure unpacked output folder is empty
        if len(os.listdir(unpacked_outputs_intermediate_dir)) != 0:
            raise OSError(f"Failed to move all contents of {unpacked_outputs_intermediate_dir} while unpacking")
        os.rmdir(unpacked_outputs_intermediate_dir)
    else:
        raise NotImplementedError(f"Output type {output_type} unpacking is not implemented")

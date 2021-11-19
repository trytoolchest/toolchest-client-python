from distutils.dir_util import copy_tree
from enum import Enum
import os
from pathlib import Path
import shutil


class OutputType(Enum):
    GZ_TAR = ".tar.gz"
    FLAT_TEXT = ".txt"


def link_dst_unlink_src(src, dst):
    """Hard links files within src to dst, and then unlinks the src. dst must be a parent of src."""
    src_path = Path(src)
    dst_path = Path(dst)
    if dst_path not in src_path.parents:
        raise ValueError("Destination path must be a parent of source path")
    # Hard link up a directory, unlink source
    for root, directories, files in os.walk(src, topdown=True):
        for file in files:
            source_file_path = f"{root}/{file}"
            new_file_path = f"{root}/{file}".replace(src, dst)  # only works if dst is a parent of src
            # Overwrite existing files if they exist
            if os.path.isfile(new_file_path):
                os.remove(new_file_path)
            os.link(source_file_path, new_file_path)
            os.unlink(source_file_path)
        for directory in directories:
            new_dir_path = directory.replace(src, dst)
            os.makedirs(new_dir_path, exist_ok=True)
    # Remove empty directories from source
    for root, directories, files in os.walk(src, topdown=False):
        if len(files) != 0:
            raise ValueError("Files were not moved successfully!")
        for directory in directories:
            os.rmdir(f"{root}/{directory}")
    os.rmdir(src)


def unpack_files(file_path_to_unpack, output_type):
    """Unpack output file, if needed. Returns the path to the (optionally) unpacked output."""
    if output_type == OutputType.FLAT_TEXT:
        # Flat text needs no post-processing
        return file_path_to_unpack
    elif output_type == OutputType.GZ_TAR:
        # The underlying shutil code does some, but it's limited
        unpacked_outputs_final_destination = os.path.dirname(file_path_to_unpack)
        # Make sure the directory is empty except for the GZ_TAR
        visible_files_in_directory = [
            f for f in os.listdir(unpacked_outputs_final_destination) if not f.startswith('.')
        ]
        if visible_files_in_directory != 1:
            raise ValueError(
                f"{unpacked_outputs_final_destination} is not empty. Please use an empty directory for output!"
            )
        shutil.unpack_archive(
            filename=file_path_to_unpack,
            extract_dir=unpacked_outputs_final_destination,
            format="gztar",
        )

        # Assumes the resulting unpacked archive is named "output", which is true by spec
        unpacked_outputs_intermediate_dir = f"{unpacked_outputs_final_destination}/output"
        # Move everything up one directory out of the temporary dir
        link_dst_unlink_src(
            src=unpacked_outputs_intermediate_dir,
            dst=unpacked_outputs_final_destination,
        )

        # Remove the unpacked .tar.gz file and empty unpacked output folder
        os.remove(file_path_to_unpack)
        # Ensure unpacked output folder is empty
        if len(os.listdir(unpacked_outputs_intermediate_dir)) != 0:
            raise OSError(f"Failed to move all contents of {unpacked_outputs_intermediate_dir} while unpacking")
        os.rmdir(unpacked_outputs_intermediate_dir)
    else:
        raise NotImplementedError(f"Output type {output_type} unpacking is not implemented")

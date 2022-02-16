import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

KRAKEN2_SINGLE_END_HASH = 886254946


@pytest.mark.integration
def test_kraken2_output_manual_download():
    """
    Tests Kraken 2 against the standard (v1) database, with
    output manually downloaded after job completion
    """
    test_dir = "test_kraken2_output_manual_download"
    input_file_s3_uri = "s3://toolchest-integration-tests/synthetic_bacteroides_reads.fasta"
    manual_output_dir_path = f"./{test_dir}/manual/"
    manual_output_file_path = f"{manual_output_dir_path}kraken2_output.txt"
    toolchest_s3_dir_path = f"./{test_dir}/toolchest/s3/"
    toolchest_s3_file_path = f"{toolchest_s3_dir_path}kraken2_output.txt"
    toolchest_pipeline_dir_path = f"./{test_dir}/toolchest/id/"
    toolchest_pipeline_file_path = f"{toolchest_pipeline_dir_path}kraken2_output.txt"

    # Run job without downloading
    output = toolchest.kraken2(
        inputs=input_file_s3_uri,
    )

    # Manually invoke download from output
    path_from_manual_download = output.download(manual_output_dir_path)

    # If multiple files are returned, path_from_manual download will be a list,
    # so we simply check if kraken2_output.txt is contained in it
    if isinstance(path_from_manual_download, list):
        path_from_manual_download = [os.path.abspath(path) for path in path_from_manual_download]
    else:
        path_from_manual_download = [path_from_manual_download]
    assert os.path.abspath(manual_output_file_path) in path_from_manual_download
    assert hash.unordered(manual_output_file_path) == KRAKEN2_SINGLE_END_HASH

    # Test again with toolchest.download(), using S3 URI
    path_from_toolchest_download = toolchest.download(toolchest_s3_dir_path, s3_uri=output.s3_uri)
    if isinstance(path_from_toolchest_download, list):
        path_from_toolchest_download = [os.path.abspath(path) for path in path_from_toolchest_download]
    else:
        path_from_toolchest_download = [path_from_toolchest_download]
    assert os.path.abspath(toolchest_s3_file_path) in path_from_toolchest_download
    assert hash.unordered(toolchest_s3_file_path) == KRAKEN2_SINGLE_END_HASH

    # Test again with toolchest.download(), using pipeline segment instance ID
    PIPELINE_INDEX_IN_S3_URI = 3
    pipeline_segment_instance_id = output.s3_uri.split("/")[PIPELINE_INDEX_IN_S3_URI]
    path_from_toolchest_download = toolchest.download(
        toolchest_pipeline_dir_path,
        pipeline_segment_instance_id=pipeline_segment_instance_id,
    )
    if isinstance(path_from_toolchest_download, list):
        path_from_toolchest_download = [os.path.abspath(path) for path in path_from_toolchest_download]
    else:
        path_from_toolchest_download = [path_from_toolchest_download]
    assert os.path.abspath(toolchest_pipeline_file_path) in path_from_toolchest_download
    assert hash.unordered(toolchest_pipeline_file_path) == KRAKEN2_SINGLE_END_HASH

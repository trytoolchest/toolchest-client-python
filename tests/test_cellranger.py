import os
import pytest
import shutil

from tests.util import s3, hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

MIN_EXPECTED_ARCHIVE_SIZE = 34000000
MAX_EXPECTED_ARCHIVE_SIZE = 38000000

EXPECTED_SUMMARY_SIZE = 2744825
EXPECTED_RAW_MATRIX_SIZE = 868393
EXPECTED_RAW_MATRIX_HASH = "d00cca1d2b4344b03946eeaeedc17ed5"
EXPECTED_FILTERED_MATRIX_SIZE = 503956


@pytest.mark.integration
def test_cellranger_count():
    test_dir = "test_cellranger_count"
    input_dir_path = f"./{test_dir}/inputs/"
    output_dir_path = f"./{test_dir}/output/"
    os.makedirs(input_dir_path, exist_ok=True)
    os.makedirs(output_dir_path, exist_ok=True)

    # Test using a compressed archive in S3
    output = toolchest.cellranger_count(
        inputs="s3://toolchest-integration-tests/cellranger/count/pbmc_1k_v3_fastqs_trimmed.tar.gz",
        transcriptome_name="GRCh38",
    )
    verify_cellranger_count_outputs(output, output_dir_path)

    shutil.rmtree(output_dir_path)
    os.makedirs(output_dir_path, exist_ok=True)

    # Test from a directory of local inputs
    packed_inputs_path = f"./{test_dir}/inputs.tar.gz"
    s3.download_integration_test_input(
        s3_file_key="cellranger/count/pbmc_1k_v3_fastqs_trimmed.tar.gz",
        output_file_path=packed_inputs_path,
    )
    shutil.unpack_archive(packed_inputs_path, input_dir_path)
    output = toolchest.cellranger_count(
        inputs=input_dir_path,
        transcriptome_name="GRCh38",
    )
    verify_cellranger_count_outputs(output, output_dir_path)


def verify_cellranger_count_outputs(output, output_dir_path):
    # Verify properties of packed archive
    archive_path = f"{output_dir_path}output.tar.gz"
    toolchest.download(
        output_path=output_dir_path,
        s3_uri=output.s3_uri,
        skip_decompression=True,
    )
    archive_size = os.path.getsize(archive_path)
    assert MIN_EXPECTED_ARCHIVE_SIZE <= archive_size <= MAX_EXPECTED_ARCHIVE_SIZE

    shutil.unpack_archive(
        filename=archive_path,
        extract_dir=output_dir_path,
        format="gztar",
    )

    # Verify properties of unpacked files
    summary_path = f"{output_dir_path}outs/web_summary.html"
    raw_matrix_path = f"{output_dir_path}outs/raw_feature_bc_matrix.h5"
    filtered_matrix_path = f"{output_dir_path}outs/filtered_feature_bc_matrix.h5"
    assert os.path.getsize(summary_path) == EXPECTED_SUMMARY_SIZE
    assert os.path.getsize(raw_matrix_path) == EXPECTED_RAW_MATRIX_SIZE
    assert os.path.getsize(filtered_matrix_path) == EXPECTED_FILTERED_MATRIX_SIZE
    assert hash.binary_hash(raw_matrix_path) == EXPECTED_RAW_MATRIX_HASH

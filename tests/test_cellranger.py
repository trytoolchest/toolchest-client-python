import os
import pytest
import shutil

from tests.util import s3, hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_cellranger_count_s3_inputs():
    test_dir = "temp_test_cellranger_count_s3_inputs"
    output_dir_path = f"./{test_dir}/output/"

    # Test using an S3 prefix containing 3 FASTQs
    output = toolchest.cellranger_count(
        inputs="s3://toolchest-integration-tests/cellranger/count/pbmc_1k_v3_fastqs_trimmed",
        database_name="GRCh38",
        output_path=output_dir_path,
        skip_decompression=True,
    )
    verify_cellranger_count_outputs(output.output_file_paths, output_dir_path)


@pytest.mark.integration
def test_cellranger_count_local_inputs():
    test_dir = "temp_test_cellranger_count_local_inputs"
    input_dir_path = f"./{test_dir}/inputs/"
    output_dir_path = f"./{test_dir}/output/"
    os.makedirs(input_dir_path, exist_ok=True)

    # Test from a directory of local inputs
    input_file_names = [
        "pbmc_1k_v3_trimmed_S1_L001_I1_001.fastq",
        "pbmc_1k_v3_trimmed_S1_L001_R1_001.fastq",
        "pbmc_1k_v3_trimmed_S1_L001_R2_001.fastq",
    ]
    for input_file_name in input_file_names:
        s3.download_integration_test_input(
            s3_file_key=f"cellranger/count/pbmc_1k_v3_fastqs_trimmed/{input_file_name}",
            output_file_path=f"{input_dir_path}/{input_file_name}",
        )
    output = toolchest.cellranger_count(
        inputs=input_dir_path,
        database_name="GRCh38",
        output_path=output_dir_path,
        skip_decompression=True,
    )
    verify_cellranger_count_outputs(output.output_file_paths, output_dir_path)


def verify_cellranger_count_outputs(archive_path, output_dir_path):
    # Expected properties of outputs
    MIN_EXPECTED_ARCHIVE_SIZE = 34000000
    MAX_EXPECTED_ARCHIVE_SIZE = 38000000
    EXPECTED_SUMMARY_SIZE = 2744825
    EXPECTED_RAW_MATRIX_SIZE = 868393
    EXPECTED_RAW_MATRIX_HASH = "d00cca1d2b4344b03946eeaeedc17ed5"
    EXPECTED_FILTERED_MATRIX_SIZE = 503956

    # Verify properties of packed archive
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

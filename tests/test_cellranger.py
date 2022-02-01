import os
import pytest
import shutil

from tests.util import s3, hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

@pytest.mark.integration
def test_cellranger_count():
    test_dir = "test_cellranger_count"
    input_dir_path = f"./{test_dir}/inputs/"
    output_dir_path = f"./{test_dir}/output/"
    output_file_path = f"{output_dir_path}output.tar.gz"
    os.makedirs(input_dir_path, exist_ok=True)
    os.makedirs(output_dir_path, exist_ok=True)

    # Test using a compressed archive in S3
    output = toolchest.cellranger_count(
        inputs="s3://toolchest-integration-tests/cellranger/count/pbmc_1k_v3_fastqs_trimmed.tar.gz",
        transcriptome_name="GRCh38",
    )
    toolchest.download(
        output_path=output,
        s3_uri=output.s3_uri,
        skip_decompression=True,
    )
    # Hash test here

    # Test from a directory of local inputs
    packed_inputs_path = f"{input_dir_path}/inputs.tar.gz"
    s3.download_integration_test_input(
        s3_file_key="cellranger/count/pbmc_1k_v3_fastqs_trimmed.tar.gz",
        output_file_path=packed_inputs_path,
    )
    shutil.unpack_archive(packed_inputs_path, input_dir_path)
    output = toolchest.cellranger_count(
        inputs=input_dir_path,
        transcriptome_name="GRCh38",
    )
    toolchest.download(
        output_path=output,
        s3_uri=output.s3_uri,
        skip_decompression=True,
    )
    # Hash test here



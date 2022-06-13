import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

DEFAULT_BLASTP_OUTPUT_HASH = 952562472
DEFAULT_BLASTX_OUTPUT_HASH = 883070112


@pytest.mark.integration
def test_diamond_blastp_standard():
    """
    Tests Diamond blastp mode
    """
    test_dir = "test_diamond_blastp_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_name = "sample_output.tsv"
    output_file_path = f"{output_dir_path}/{output_file_name}"

    toolchest.diamond_blastp(
        inputs="s3://toolchest-integration-tests/diamond_blastp_input.fa",
        output_path=output_dir_path,
        output_primary_name=output_file_name,
    )

    assert hash.unordered(output_file_path) == DEFAULT_BLASTP_OUTPUT_HASH


@pytest.mark.integration
def test_diamond_blastx_standard():
    """
    Tests Diamond blastx mode
    """
    test_dir = "test_diamond_blastx_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_name = "sample_output.tsv"
    output_file_path = f"{output_dir_path}/{output_file_name}"

    toolchest.diamond_blastx(
        inputs="s3://toolchest-integration-tests/sample_r1_shortened.fastq",
        output_path=output_dir_path,
        output_primary_name=output_file_name,
    )

    assert hash.unordered(output_file_path) == DEFAULT_BLASTX_OUTPUT_HASH

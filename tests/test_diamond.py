import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

DEFAULT_OUTPUT_HASH = 952562472

@pytest.mark.integration
def test_diamond_blastp_standard():
    """
    Tests Diamond blastp mode
    """
    test_dir = "test_diamond_blastp_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}/"
    output_file_path = f"{output_dir_path}sample_output.tsv"

    toolchest.diamond_blastp(
        inputs="s3://toolchest-integration-tests/diamond_blastp_input.fa",
        output_path=output_file_path,
    )

    assert hash.unordered(output_file_path) == DEFAULT_OUTPUT_HASH

import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_clustalo_standard():
    """
    Tests Clustal Omega
    """
    test_dir = "temp_test_clustalo_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_name = "sample_output.fasta"
    output_file_path = f"{output_dir_path}/{output_file_name}"

    toolchest.clustalo(
        inputs="s3://toolchest-integration-tests/clustalo_input.fasta",
        output_path=output_dir_path,
        output_primary_name=output_file_name,
    )

    assert hash.unordered(output_file_path) == 1217555147

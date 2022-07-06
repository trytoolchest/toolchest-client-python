import os
import pytest

from tests.util import hash
import toolchest_client as toolchest


toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_blastn_nt():
    """
    Tests BLASTN against the default nt (v1) DB
    """
    test_dir = "temp_test_blastn_nt"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/blastn_results.out"

    toolchest.blastn(
        inputs="s3://toolchest-integration-tests/small_synthetic_bacteroides_reads.fasta",
        output_path=output_dir_path,
        tool_args="-mt_mode 1"
    )

    assert hash.unordered(output_file_path) == 1290536116

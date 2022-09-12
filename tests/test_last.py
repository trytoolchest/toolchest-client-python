import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_lastal5():
    """
    Tests lastal5 against the standard database
    """
    test_dir = "temp_test_lastal5_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/out.maf"

    toolchest.lastal5(
        inputs="s3://toolchest-integration-tests/synthetic_bacteroides_reads.fasta",
        output_path=output_dir_path,
        tool_args="-m50"
    )

    assert hash.unordered(output_file_path) == 927021088

import os
import pytest

os.environ["TOOLCHEST_API_URL"] = "https://staging.api.toolche.st"

import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_transfer_http():
    """
    Tests transfer function with an http input
    """
    test_dir = "temp_test_transfer_http"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/P48754.fasta"

    toolchest.transfer(
        inputs="https://rest.uniprot.org/uniprotkb/P48754.fasta",
        output_path=output_dir_path
    )

    with open(output_file_path, "r") as f:
        assert f.read().startswith(">sp|P48754|BRCA1_MOUSE")

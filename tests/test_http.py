import os
import pytest

import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_http_input():
    """
    Tests test function with an http input
    """
    test_dir = "test_http"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_file_path = "https://toolchest-public-examples-no-encryption.s3.amazonaws.com/example.fastq"
    output_dir_path = f"./{test_dir}/"
    output_file_path = f"{output_dir_path}test_output.txt"

    toolchest.test(
        inputs=input_file_path,
        output_path=output_dir_path
    )

    with open(output_file_path, "r") as f:
        for line in f:
            assert line == "success"

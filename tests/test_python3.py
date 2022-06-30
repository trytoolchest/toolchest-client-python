import os
import pytest

import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_python3():
    """
    Tests python3 tool's inputs, output, and tool_arg
    """

    test_dir = "./temp_test_python3"
    os.makedirs(f"{test_dir}", exist_ok=True)
    toolchest.python3(
        tool_args=f"./input/example.fastq",
        script="s3://toolchest-integration-tests/write_test.py",
        inputs="s3://toolchest-integration-tests/example.fastq",
        output_path=f"{test_dir}/",
    )

    output_file = open(f"{test_dir}/output.txt", "r")
    assert output_file.readline() == "Success"
    output_file.close()

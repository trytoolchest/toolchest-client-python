import os
import pytest

import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_output_object():
    """
    Verifies that the output object has all the desired parameters.
    """
    test_dir = "temp_test_output_object"
    input_file_s3_uri = "s3://toolchest-integration-tests/small_synthetic_bacteroides_reads.fasta"
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/test_output.txt"
    os.makedirs(output_dir_path, exist_ok=True)

    toolchest_output = toolchest.test(
        inputs=input_file_s3_uri,
        output_path=output_dir_path
    )

    print(toolchest_output)
    assert toolchest_output.tool_name == "test"
    assert toolchest_output.tool_version == "0.1.0"
    assert toolchest_output.database_name is None
    assert toolchest_output.database_version is None
    assert toolchest_output.run_id is not None
    assert toolchest_output.output_path == os.path.abspath(output_dir_path)
    assert toolchest_output.output_file_paths == os.path.abspath(output_file_path)

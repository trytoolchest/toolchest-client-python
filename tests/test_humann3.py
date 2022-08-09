import os
import pytest

import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_humann3():
    """
    Tests humann3
    """

    test_dir = "temp_test_humann3_default"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}/"

    toolchest.humann3(
        inputs="s3://toolchest-integration-tests/humann3/demo.m8",
        # inputs="s3://toolchest-integration-tests-private/humann3/test_R1.fastq",
        output_path=output_dir_path,
    )



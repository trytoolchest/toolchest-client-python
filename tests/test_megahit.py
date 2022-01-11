import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

@pytest.mark.integration
def test_megahit_one_pair():
    """
    Tests Megahit with a single pair of paired-end inputs.

    Note: Multithreaded megahit is not deterministic, so
    we check the size of the file instead.
    See https://github.com/voutcn/megahit/issues/48.
    """
    test_dir = "test_megahit_one_pair"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}/"
    # output_file_path = f"{output_dir_path}kraken2_output.txt"

    output = toolchest.megahit(
        interleaved=[
            "s3://toolchest-integration-tests-public/megahit/r1.il.fa.gz",
            "s3://toolchest-integration-tests-public/megahit/r2.il.fa.bz2",
        ],
        read_one="s3://toolchest-integration-tests-public/megahit/r3_1.fa",
        read_two="s3://toolchest-integration-tests-public/megahit/r3_2.fa",
        single_end=[
            "s3://toolchest-integration-tests-public/megahit/r4.fa",
            "s3://toolchest-integration-tests-public/megahit/loop.fa",
        ],
        tool_args="--presets meta-large",
        output_path=output_dir_path,
    )

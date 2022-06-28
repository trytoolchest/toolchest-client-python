import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

SHI7_SINGLE_END_HASH = 1570879637
SHOGUN_CHAINED_HASH = 1708070294


@pytest.mark.integration
def test_shi7_shogun_chaining():
    """
    Tests S3-based chaining with shi7 and shogun. Passes the S3 URI of the
    shi7 output to shogun as input, skipping the (intermediate) shi7 output download.
    Downloads the (final) shogun output to hash for testing.

    To enforce shi7 determinism, a single R1 input is used.

    Note: This test also tests the Output object generated by the shi7() tool call,
    and chaining the shi7 output files depends on how the Output is structured.
    If the Output class is modified, this test should be modified as well.
    """

    test_dir = "temp_test_shi7_shogun_chaining"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path_shogun = f"{output_dir_path}/alignment.bowtie2.sam"

    output_shi7 = toolchest.shi7(
        tool_args="-SE",
        inputs="s3://toolchest-integration-tests/sample_r1.fastq.gz",
    )

    # Note: since output_path was omitted from the shi7 function call,
    # local download is skipped, and the local output_path of output_shi7
    # should be None.
    assert output_shi7.output_path is None

    output_shogun = toolchest.shogun_align(
        inputs=output_shi7.s3_uri,
        output_path=output_dir_path,
    )

    assert hash.unordered(output_file_path_shogun) == SHOGUN_CHAINED_HASH
    assert hash.unordered(output_shogun.output_path) == SHOGUN_CHAINED_HASH

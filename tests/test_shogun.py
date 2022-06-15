import os
import pytest

from tests.util import s3, hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_shogun_filter_and_align():
    """
    Tests shogun (filter and align for simplicity) with a single R1 input
    """

    test_dir = "./test_shogun_filter_and_align"
    os.makedirs(f"{test_dir}", exist_ok=True)
    input_file_path = f"{test_dir}/combined_seqs_unfiltered.fna"
    output_file_path_filter = f"{test_dir}/combined_seqs.filtered.fna"
    output_file_path_align = f"{test_dir}/alignment.bowtie2.sam"

    s3.download_integration_test_input(
        s3_file_key="combined_seqs_unfiltered.fna",
        output_file_path=input_file_path,
        is_private=True,
    )

    toolchest.shogun_filter(
        tool_args="--alignment True",
        inputs=input_file_path,
        output_path=test_dir,
    )

    assert hash.unordered(output_file_path_filter) == 510167908

    toolchest.shogun_align(
        tool_args="",
        inputs=output_file_path_filter,
        output_path=test_dir,
    )
    assert hash.unordered(output_file_path_align) == 1952162202

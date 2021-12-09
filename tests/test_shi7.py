import os
import pytest

from tests.util import s3, hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

# Because shi7 paired-end is non-deterministic, we just make sure it's not equal to the single-end version
SHI7_SINGLE_END_HASH = 1570879637


@pytest.mark.skip(reason="Not yet productionized")
def test_shi7_single_end():
    """
    Tests shi7 with a single R1 input
    """

    test_dir = "test_shi7_single_end"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_one_file_path = f"./{test_dir}/shi7_input_R1.fastq.gz"
    output_file_path = f"./{test_dir}/combined_seqs.fna"

    s3.download_integration_test_input(
        s3_file_key="sample_r1.fastq.gz",
        output_file_path=input_one_file_path,
    )

    toolchest.shi7(
        tool_args="-SE",
        inputs=f"./{test_dir}",
        output_path=output_file_path,
    )

    assert hash.unordered(output_file_path) == SHI7_SINGLE_END_HASH


@pytest.mark.skip(reason="Not yet productionized")
def test_shi7_paired_end():
    """
    Tests shi7 with paired-end inputs

    Unfortunately, shi7 is non-deterministic. This means we can't check a hash.
    As a means of having some level of guarantee, we check the output file size instead.

    Because of this, we should not recommend shi7 for use.
    """

    test_dir = "test_shi7_paired_end"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_one_file_path = f"./{test_dir}/shi7_input_R1.fastq.gz"
    input_two_file_path = f"./{test_dir}/shi7_input_R2.fastq.gz"
    output_file_path = f"./{test_dir}/combined_seqs.fna"

    s3.download_integration_test_input(
        s3_file_key="sample_r1.fastq.gz",
        output_file_path=input_one_file_path,
    )
    s3.download_integration_test_input(
        s3_file_key="sample_r2.fastq.gz",
        output_file_path=input_two_file_path,
    )

    toolchest.shi7(
        inputs=f"./{test_dir}",
        output_path=output_file_path,
    )

    # Because shi7 paired-end is non-deterministic, we just make sure it's not equal to the single-end version
    assert hash.unordered(output_file_path) != SHI7_SINGLE_END_HASH
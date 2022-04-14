import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

DEFAULT_OUTPUT_HASH = 1022436992


@pytest.mark.integration
def test_diamond_blastp_standard():
    """
    Tests Unicycler
    """
    test_dir = "test_diamond_blastp_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}/"

    toolchest.unicycler(
        output_path=output_dir_path,
        read_one="s3://toolchest-integration-tests/r1.fastq.gz",
        read_two="s3://toolchest-integration-tests/r2.fastq.gz",
        long_reads="s3://toolchest-integration-tests/long_reads.fasta.gz"
    )

    assert hash.unordered(f"{output_dir_path}assembly.fasta") == DEFAULT_OUTPUT_HASH

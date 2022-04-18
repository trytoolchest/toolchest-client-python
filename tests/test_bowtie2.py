import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_bowtie2():
    """
    Tests bowtie2
    """

    test_dir = "test_bowtie2_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}/"

    toolchest.bowtie2(
        inputs="s3://toolchest-integration-tests/sample_r1.fastq.gz",
        output_path=output_dir_path,
    )

    assert hash.unordered(f"{output_dir_path}bowtie2_output.sam") == 370259722

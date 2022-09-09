import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_fastqc():
    """
    Tests FastQC with a fastq file

    """

    test_dir = "temp_test_fastqc"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"

    toolchest.fastqc(
        inputs="s3://toolchest-integration-tests/sample_r1_shortened.fastq",
        output_path=output_dir_path
    )

    assert hash.unordered(os.path.join(test_dir, "sample_r1_shortened_fastqc.html")) == 1123268405

    assert os.path.getsize(os.path.join(test_dir, "sample_r1_shortened_fastqc.zip")) == 326078

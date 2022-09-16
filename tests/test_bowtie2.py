import os
import pytest

from tests.util import hash, filter_output
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_bowtie2():
    """
    Tests bowtie2
    """

    test_dir = "temp_test_bowtie2_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/bowtie2_output.sam"
    filtered_output_file_path = f"{output_dir_path}/bowtie2_output.filtered.sam"

    toolchest.bowtie2(
        inputs="s3://toolchest-integration-tests/DRR000006.fastq.gz",
        output_path=output_dir_path,
    )

    # Filter non-deterministic metadata lines
    filter_output.filter_sam(output_file_path, filtered_output_file_path)
    assert hash.unordered(filtered_output_file_path) == 1444969892

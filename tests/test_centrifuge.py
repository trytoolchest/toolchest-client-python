import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_centrifuge_many_types():
    """
    Tests Centrifuge with one pair of paired-end inputs and two single-end inputs.
    """
    test_dir = "temp_test_centrifuge/many_types"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/centrifuge_output.txt"
    output_report_path = f"{output_dir_path}/centrifuge_report.tsv"

    toolchest.centrifuge(
        read_one="s3://toolchest-integration-tests/megahit/r3_1.fa",  # TODO: find centrifuge-specific files
        read_two="s3://toolchest-integration-tests/megahit/r3_2.fa",
        unpaired=[
            "s3://toolchest-integration-tests/megahit/r4.fa",
            "s3://toolchest-integration-tests/megahit/loop.fa",
        ],
        output_path=output_dir_path,
    )

    assert os.path.exists(output_report_path)
    assert hash.unordered(output_file_path)  # TODO: check value


@pytest.mark.integration
def test_centrifuge_multiple_pairs():
    """
    Tests Centrifuge with two pairs of paired-end inputs.
    """
    test_dir = "temp_test_centrifuge/multiple_pairs"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/centrifuge_output.txt"
    output_report_path = f"{output_dir_path}/centrifuge_report.tsv"

    toolchest.centrifuge(
        read_one=[
            "s3://toolchest-integration-tests/megahit/r3_1.fa",  # TODO: find centrifuge-specific files
            "s3://toolchest-integration-tests/r1.fastq.gz",
        ],
        read_two=[
            "s3://toolchest-integration-tests/megahit/r3_2.fa",
            "s3://toolchest-integration-tests/r2.fastq.gz",
        ],
        output_path=output_dir_path,
    )

    assert os.path.exists(output_report_path)
    assert hash.unordered(output_file_path)  # TODO: check value

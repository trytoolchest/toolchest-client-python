import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

EXPECTED_MIN_OUTPUT_SIZE_MANY_TYPES = 1000
EXPECTED_MIN_OUTPUT_SIZE_TWO_PAIRS = 3 * 1024 * 1024


@pytest.mark.integration
def test_megahit_many_types():
    """
    Tests Megahit with two interleaved inputs, one pair of paired-end inputs,
    and two single-end inputs.

    Note: Multithreaded megahit is not deterministic, so
    we check the size of the file instead.
    See https://github.com/voutcn/megahit/issues/48.
    """
    test_dir = "test_megahit_many_types"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}/"
    output_file_path = f"{output_dir_path}final.contigs.fa"

    toolchest.megahit(
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

    assert os.path.getsize(output_file_path) >= EXPECTED_MIN_OUTPUT_SIZE_MANY_TYPES


@pytest.mark.integration
def test_megahit_multiple_pairs():
    """
    Tests Megahit with two pairs of paired-end inputs.

    Note: Multithreaded megahit is not deterministic, so
    we check the size of the file instead.
    See https://github.com/voutcn/megahit/issues/48.
    """
    test_dir = "test_megahit_two_pairs"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}/"
    output_file_path = f"{output_dir_path}final.contigs.fa"

    toolchest.megahit(
        read_one=[
            "s3://toolchest-integration-tests-public/megahit/r3_1.fa",
            "s3://toolchest-integration-tests-public/r1.fastq.gz",
        ],
        read_two=[
            "s3://toolchest-integration-tests-public/megahit/r3_2.fa",
            "s3://toolchest-integration-tests-public/r2.fastq.gz",
        ],
        tool_args="--presets meta-large",
        output_path=output_dir_path,
    )

    assert os.path.getsize(output_file_path) >= EXPECTED_MIN_OUTPUT_SIZE_TWO_PAIRS

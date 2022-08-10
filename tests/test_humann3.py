import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_humann3_m8():
    """
    Tests humann3 with an m8 file
    Note: This test skips the alignment step.
    """

    test_dir = "temp_test_humann3_m8"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_genefamilies_path = f"{output_dir_path}/demo_genefamilies.tsv"
    output_pathabundance_path = f"{output_dir_path}/demo_pathabundance.tsv"
    output_pathcoverage_path = f"{output_dir_path}/demo_pathcoverage.tsv"

    toolchest.humann3(
        inputs="s3://toolchest-integration-tests/humann3/demo.m8",
        output_path=output_dir_path,
    )

    assert hash.unordered(output_genefamilies_path) == 917720334
    assert hash.unordered(output_pathabundance_path) == 1938423861
    assert hash.unordered(output_pathcoverage_path) == 1315086232


@pytest.mark.integration_full
def test_humann3_fastq():
    """
    Tests humann3 with a fastq.gz file
    Note: This test takes about 1 hour and should be run on pre-deploy tests only.
    """

    test_dir = "temp_test_humann3_fastq"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_genefamilies_path = f"{output_dir_path}/demo_genefamilies.tsv"
    output_pathabundance_path = f"{output_dir_path}/demo_pathabundance.tsv"
    output_pathcoverage_path = f"{output_dir_path}/demo_pathcoverage.tsv"

    toolchest.humann3(
        inputs="s3://toolchest-integration-tests/humann3/demo.fastq.gz",
        output_path=output_dir_path,
    )

    # Assert existence
    assert os.path.exists(output_genefamilies_path)
    assert os.path.exists(output_pathabundance_path)
    assert os.path.exists(output_pathcoverage_path)

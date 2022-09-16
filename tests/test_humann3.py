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

    renamed_genefamilies_name = "renamed_demo_genefamilies.tsv"
    renamed_genefamilies_path = f"{output_dir_path}/{renamed_genefamilies_name}"
    toolchest.humann3(
        mode=toolchest.tools.humann.HUMAnN3Mode.HUMANN_RENAME_TABLE,
        inputs=output_genefamilies_path,
        tool_args="--names uniref50",
        output_primary_name=renamed_genefamilies_name,
        output_path=output_dir_path,
    )

    assert hash.unordered(renamed_genefamilies_path) == 417465229


@pytest.mark.integration
def test_humann3_fastq():
    """
    Tests humann3 with a fastq.gz file
    Note: This test uses taxonomic profile (from running the same input without one) to speed up execution. This skips
    some steps that would otherwise happen but cause the test to take around an hour.
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
        taxonomic_profile="s3://toolchest-integration-tests/humann3/demo_metaphlan_bugs_list.tsv",
    )

    # Assert existence
    assert os.path.exists(output_genefamilies_path)
    assert os.path.exists(output_pathabundance_path)
    assert os.path.exists(output_pathcoverage_path)

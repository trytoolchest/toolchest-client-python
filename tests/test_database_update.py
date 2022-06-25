import os
import time
import pytest

import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_database_update_s3():
    """
    Tests custom database update for Kraken 2 and the standard database
    """
    output = toolchest.update_database(
        database_path="s3://toolchest-integration-tests/arbitrary_directory/",
        tool=toolchest.tools.Kraken2,
        database_name="standard",
    )

    assert output.database_name == "standard"
    assert output.database_version


@pytest.mark.integration
def test_database_update_local():
    """
    Tests custom database update for diamond blastp using a local file
    """
    test_dir = "test_database_update_local"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    test_file_one = f"{test_dir}/test.fasta"
    test_file_two = f"{test_dir}/test.fastq"

    open(test_file_one, "w").close()
    open(test_file_two, "w").close()

    output = toolchest.update_database(
        database_path=test_dir,
        tool=toolchest.tools.Kraken2,
        database_name="standard",
    )

    assert output.database_name == "standard"
    assert output.database_version


@pytest.mark.integration
def test_database_add_s3():
    """
    Tests custom database addition for Kraken 2
    """
    output = toolchest.add_database(
        database_path="s3://toolchest-integration-tests/arbitrary_directory/",
        tool=toolchest.tools.Kraken2,
        database_name=f"new_name_{time.time()}",
    )

    print(output)

    assert output.database_name.startswith("new_name_")
    assert output.database_version == "1"

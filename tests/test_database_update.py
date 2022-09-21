import os
import time
import pytest

from tests.util import s3, hash, filter_output
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_database_update_s3():
    """
    Tests custom database update for bowtie 2 using S3 files.
    Runs 2 update tests in sequence. The second part tests using
    an S3 prefix and auto-generated primary name.
    """
    # Part 1: test using explicitly listed files and primary name
    listed_files_test_dir = "temp_test_db_update_s3_bowtie2"
    os.makedirs(f"./{listed_files_test_dir}", exist_ok=True)
    output_dir_path = f"./{listed_files_test_dir}"

    # Update DB
    update_db_output = toolchest.update_database(
        database_path=[
            "s3://toolchest-integration-tests/databases/bowtie2-fruitfly-Dmel/Dmel_A4_1.0.1.bt2",
            "s3://toolchest-integration-tests/databases/bowtie2-fruitfly-Dmel/Dmel_A4_1.0.2.bt2",
            "s3://toolchest-integration-tests/databases/bowtie2-fruitfly-Dmel/Dmel_A4_1.0.3.bt2",
            "s3://toolchest-integration-tests/databases/bowtie2-fruitfly-Dmel/Dmel_A4_1.0.4.bt2",
            "s3://toolchest-integration-tests/databases/bowtie2-fruitfly-Dmel/Dmel_A4_1.0.rev.1.bt2",
            "s3://toolchest-integration-tests/databases/bowtie2-fruitfly-Dmel/Dmel_A4_1.0.rev.2.bt2",
        ],
        tool=toolchest.tools.Bowtie2,
        database_name="integration_test_bowtie2_fruitfly",
        database_primary_name="Dmel_A4_1.0",
        is_async=False,  # to ensure DB finishes uploading before tool call
    )
    assert update_db_output.database_name == "integration_test_bowtie2_fruitfly"
    assert update_db_output.database_version

    run_and_test_bowtie2_on_updated_db(
        expected_hash=107700257,
        output_dir_path=output_dir_path,
        update_db_output=update_db_output
    )

    # Part 2: test using an S3 prefix and assumed primary name
    prefix_test_dir = "temp_test_db_update_s3_prefix_bowtie2"
    os.makedirs(f"./{prefix_test_dir}", exist_ok=True)
    output_dir_path = f"./{prefix_test_dir}"

    # Update DB
    # This should be the same Dmel_A4_1.0 database
    update_db_output = toolchest.update_database(
        database_path="s3://toolchest-public-examples-no-encryption/integration-test-db/bowtie2-fruitfly",
        tool=toolchest.tools.Bowtie2,
        database_name="integration_test_bowtie2_fruitfly",
        is_async=False,  # to ensure DB finishes uploading before tool call
    )
    assert update_db_output.database_name == "integration_test_bowtie2_fruitfly"
    assert update_db_output.database_version

    run_and_test_bowtie2_on_updated_db(
        expected_hash=107700257,
        output_dir_path=output_dir_path,
        update_db_output=update_db_output
    )


@pytest.mark.integration
def test_database_update_local():
    """
    Tests custom database update for bowtie 2 using local files
    """
    test_dir = "temp_test_db_update_local_bowtie2"
    input_dir_path = f"./{test_dir}/inputs/"
    input_file_names = [
        "BDGP6.1.bt2",
        "BDGP6.2.bt2",
        "BDGP6.3.bt2",
        "BDGP6.4.bt2",
        "BDGP6.rev.1.bt2",
        "BDGP6.rev.2.bt2",
    ]
    output_dir_path = f"./{test_dir}"
    os.makedirs(input_dir_path, exist_ok=True)

    # Download DB files
    for input_file_name in input_file_names:
        s3.download_integration_test_input(
            s3_file_key=f"databases/bowtie2-fruitfly-BDGP6/{input_file_name}",
            output_file_path=f"{input_dir_path}{input_file_name}",
        )

    # Update DB
    update_db_output = toolchest.update_database(
        database_path=input_dir_path,
        tool=toolchest.tools.Bowtie2,
        database_name="integration_test_bowtie2_fruitfly",
        database_primary_name="BDGP6",
        is_async=False,  # to ensure DB finishes uploading before tool call
    )
    assert update_db_output.database_name == "integration_test_bowtie2_fruitfly"
    assert update_db_output.database_version

    # Run job on updated DB
    run_and_test_bowtie2_on_updated_db(
        expected_hash=1936736537,
        output_dir_path=output_dir_path,
        update_db_output=update_db_output
    )


@pytest.mark.integration
def test_database_add_s3():
    """
    Tests custom database addition for Kraken 2
    """
    KRAKEN2_OUTPUT_VIRAL_HASH = 1003212151

    test_dir = "temp_test_db_add_kraken2_viral"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/kraken2_output.txt"

    # Add database
    add_db_output = toolchest.add_database(
        database_path="s3://toolchest-public-examples-no-encryption/integration-test-db/kraken2-viral/",
        tool=toolchest.tools.Kraken2,
        database_name=f"integration_test_kraken2_viral_{time.time()}",
        is_async=False,  # to ensure DB finishes uploading before tool call
        database_primary_name=None,
    )
    assert add_db_output.database_name.startswith("integration_test_kraken2_viral")
    assert add_db_output.database_version == "1"

    # Run test input on new database
    toolchest.kraken2(
        read_one="s3://toolchest-integration-tests/synthetic_bacteroides_reads.fasta",
        database_name=add_db_output.database_name,
        database_version=add_db_output.database_version,
        output_path=output_dir_path,
    )
    assert hash.unordered(output_file_path) == KRAKEN2_OUTPUT_VIRAL_HASH


def run_and_test_bowtie2_on_updated_db(
        expected_hash,
        output_dir_path,
        update_db_output,
):
    """Tests a Bowtie 2 run on the updated DB."""
    output_file_path = f"{output_dir_path}/bowtie2_output.sam"
    filtered_output_file_path = f"{output_dir_path}/bowtie2_output.filtered.sam"

    toolchest.bowtie2(
        inputs="s3://toolchest-integration-tests/bowtie2/fruitfly-ncbi/GSM868349.fastq.gz",
        output_path=output_dir_path,
        database_name=update_db_output.database_name,
        database_version=update_db_output.database_version,
    )
    filter_output.filter_sam(output_file_path, filtered_output_file_path)
    assert hash.unordered(filtered_output_file_path) == expected_hash

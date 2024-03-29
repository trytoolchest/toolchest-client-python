import os
import pytest

from tests.util import s3, hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

KRAKEN2_SINGLE_END_HASH = 886254946


@pytest.mark.integration
def test_kraken2_standard():
    """
    Tests Kraken 2 against the standard (v1) database
    """
    test_dir = "temp_test_kraken2_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_file_path = "./kraken_input.fasta"
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/kraken2_output.txt"

    s3.download_integration_test_input(
        s3_file_key="synthetic_bacteroides_reads.fasta",
        output_file_path=input_file_path,
    )

    toolchest.kraken2(
        inputs=input_file_path,
        output_path=output_dir_path,
    )

    assert hash.unordered(output_file_path) == KRAKEN2_SINGLE_END_HASH


@pytest.mark.integration
def test_kraken2_paired_end():
    """
    Tests Kraken 2 with paired-end inputs against the std (v1) DB
    """
    test_dir = "temp_test_kraken2_paired_end"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_one_file_path = f"./{test_dir}/kraken_input_read1.fastq.gz"
    input_two_file_path = f"./{test_dir}/kraken_input_read2.fastq.gz"
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/kraken2_output.txt"

    s3.download_integration_test_input(
        s3_file_key="sample_r1.fastq.gz",
        output_file_path=input_one_file_path,
    )
    s3.download_integration_test_input(
        s3_file_key="sample_r2.fastq.gz",
        output_file_path=input_two_file_path,
    )

    toolchest.kraken2(
        read_one=input_one_file_path,
        read_two=input_two_file_path,
        output_path=output_dir_path,
    )

    # Kraken 2 paired-end is not completely deterministic, and consistently alternates between these two hashes
    assert hash.unordered(output_file_path) in [1076645572, 1174140935]


@pytest.mark.integration
def test_kraken2_s3_with_bracken():
    """
    Tests Kraken 2 with an example input in S3 against the std (v1) DB, with Bracken
    """
    test_dir = "temp_test_kraken2_s3"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/kraken2_output.txt"
    report_file_path = f"{output_dir_path}/kraken2_report.txt"

    toolchest.kraken2(
        inputs="s3://toolchest-integration-tests/kraken2/demo.fastq.gz",
        output_path=output_dir_path,
        database_name="standard",
        database_version="1",
    )

    assert hash.unordered(output_file_path) == 913900323
    assert hash.unordered(report_file_path) == 701943163

    bracken_primary_name = "test.bracken"

    toolchest.bracken(
        kraken2_report=report_file_path,
        output_path=output_dir_path,
        output_primary_name=bracken_primary_name,
        database_name="standard",
        database_version="1",
        tool_args="-r 150 -l G",
    )

    assert hash.unordered(os.path.join(output_dir_path, bracken_primary_name)) == 459225326


@pytest.mark.integration
def test_kraken2_custom_db():
    """
    Tests Kraken 2 with an example custom database (viral refseq index)
    """
    KRAKEN2_OUTPUT_VIRAL_HASH = 1003212151

    test_dir = "temp_test_kraken2_custom_db"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/kraken2_output.txt"

    custom_db = "s3://toolchest-fsx-databases/kraken2/k2_viral_20210517/"
    toolchest.kraken2(
        read_one="s3://toolchest-integration-tests/synthetic_bacteroides_reads.fasta",
        remote_database_path=custom_db,
        output_path=output_dir_path,
    )

    assert hash.unordered(output_file_path) == KRAKEN2_OUTPUT_VIRAL_HASH

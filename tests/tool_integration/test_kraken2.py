import os
import pytest

from tests.util import s3, hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_kraken2_standard():
    """
    Tests Kraken 2 against the standard (v1) database
    """
    test_dir = "test_kraken2_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_file_path = "./kraken_input.fasta"
    output_dir_path = f"./{test_dir}/"
    output_file_path = f"{output_dir_path}kraken2_output.txt"

    s3.download_integration_test_input(
        s3_file_key="synthetic_bacteroides_reads.fasta",
        output_file_path=input_file_path,
    )

    toolchest.kraken2(
        inputs=input_file_path,
        output_path=output_dir_path,
    )

    assert hash.unordered(output_file_path) == 886254946


@pytest.mark.integration
def test_kraken2_paired_end():
    """
    Tests Kraken 2 with paired-end inputs against the std (v1) DB
    """
    test_dir = "test_kraken2_paired_end"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_one_file_path = f"./{test_dir}/kraken_input_read1.fastq.gz"
    input_two_file_path = f"./{test_dir}/kraken_input_read2.fastq.gz"
    output_dir_path = f"./{test_dir}/"
    output_file_path = f"{output_dir_path}kraken2_output.txt"

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

    assert hash.unordered(output_file_path) == 1174140935

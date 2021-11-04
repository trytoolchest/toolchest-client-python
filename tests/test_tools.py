import os

import pytest

from .util import s3, hash

if os.environ.get("DEPLOY_ENVIRONMENT") == "staging":
    os.environ["BASE_URL"] = os.environ["TOOLCHEST_STAGING_URL"]

import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_kraken2_standard():
    """
    Tests Kraken 2 against the standard (v1) database
    """
    input_file_path = "./kraken_input.fasta"
    output_file_path = "./kraken_output.txt"

    s3.download_integration_test_input(
        s3_file_key="synthetic_bacteroides_reads.fasta",
        output_file_path=input_file_path,
    )

    toolchest.kraken2(
        inputs=input_file_path,
        output_path=output_file_path,
    )

    assert hash.unordered(output_file_path) == 886254946


@pytest.mark.integration
def test_kraken2_paired_end():
    """
    Tests Kraken 2 with paired-end inputs against the std (v1) DB
    """
    input_one_file_path = "./kraken_input_read1.fastq.gz"
    input_two_file_path = "./kraken_input_read2.fastq.gz"
    output_file_path = "./kraken_paired_output.txt"

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
        output_path=output_file_path,
    )

    assert hash.unordered(output_file_path) == 1076645572


@pytest.mark.integration_a
def test_shi7_paired_end():
    """
    Tests shi7 with paired-end inputs
    """

    test_input_dir = "shi7_test_input"
    os.makedirs(f"./{test_input_dir}", exist_ok=True)
    input_one_file_path = f"./{test_input_dir}/shi7_input_R1.fastq.gz"
    input_two_file_path = f"./{test_input_dir}/shi7_input_R2.fastq.gz"
    output_file_path = "./combined_seqs.fna"

    s3.download_integration_test_input(
        s3_file_key="sample_r1.fastq.gz",
        output_file_path=input_one_file_path,
    )
    s3.download_integration_test_input(
        s3_file_key="sample_r2.fastq.gz",
        output_file_path=input_two_file_path,
    )

    toolchest.shi7(
        inputs=f"./{test_input_dir}",
        output_path=output_file_path,
    )

    assert hash.unordered(output_file_path) == 483542209

import pytest

import os
from tests.util import s3, hash

if os.environ.get("DEPLOY_ENVIRONMENT") == "staging":
    os.environ["BASE_URL"] = os.environ["TOOLCHEST_STAGING_URL"]

import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_kraken2_standard():
    """
    Tests Kraken 2 against the standard (v1) database, with a small file
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


@pytest.mark.expensive_integration
def test_unicycler_paired_end_with_long_reads():
    """
    Tests Unicycler with paired end reads and Oxford Nanopore long reads
    """
    r1_file_path = "./r1.fastq.gz"
    r2_file_path = "./r2.fastq.gz"
    long_reads_file_path = "./long_reads.fasta.gz"
    output_file_path = "./unicycler_output.fasta"

    s3.download_integration_test_input(
        s3_file_key="r1.fastq.gz",
        output_file_path=r1_file_path,
    )
    s3.download_integration_test_input(
        s3_file_key="r2.fastq.gz",
        output_file_path=r2_file_path,
    )
    s3.download_integration_test_input(
        s3_file_key="long_reads.fasta.gz",
        output_file_path=long_reads_file_path,
    )

    toolchest.unicycler(
        read_one=r1_file_path,
        read_two=r2_file_path,
        long_reads=long_reads_file_path,
        output_path=output_file_path,
    )

    assert hash.unordered(output_file_path) == 100


@pytest.mark.expensive_integration
def test_star_hg38():
    """
    Tests STAR against the hg38 database, with a small file
    """
    input_file_path = "./small.fastq"
    output_file_path = "./star_output.sam"

    s3.download_integration_test_input(
        s3_file_key="small.fastq",
        output_file_path=input_file_path,
    )

    toolchest.STAR(
        read_one=input_file_path,
        output_path=output_file_path,
        database_name='GRCh38',
    )

    assert hash.unordered(output_file_path) == 100


@pytest.mark.expensive_integration
def test_parallel_star_hg38():
    """
    Tests STAR against the hg38 database, with a large file
    """
    input_file_path = "./large.fastq"
    output_file_path = "./parallel_star_output.sam"

    s3.download_integration_test_input(
        s3_file_key="large.fastq",
        output_file_path=input_file_path,
    )

    toolchest.STAR(
        read_one=input_file_path,
        output_path=output_file_path,
        database_name='GRCh38',
    )

    assert hash.unordered(output_file_path) == 100


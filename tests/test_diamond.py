import os
import pytest

from tests.util import hash, s3
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_diamond_blastp_standard():
    """
    Tests Diamond blastp mode
    """
    test_dir = "temp_test_diamond_blastp_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_name = "sample_output.tsv"
    output_file_path = f"{output_dir_path}/{output_file_name}"

    toolchest.diamond_blastp(
        inputs="s3://toolchest-integration-tests/diamond_blastp_input.fa",
        output_path=output_dir_path,
        output_primary_name=output_file_name,
    )

    assert hash.unordered(output_file_path) == 952562472


@pytest.mark.integration
def test_diamond_blastp_remote_database():
    """
    Tests DIAMOND BLASTP with a remote database, including a primary name
    """
    test_dir = "test_diamond_blastp_remote_database"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_name = "sample_output.tsv"
    output_file_path = f"{output_dir_path}/{output_file_name}"

    toolchest.diamond_blastp(
        inputs="s3://toolchest-integration-tests/short_diamond_blastp_input.fa",
        remote_database_path="s3://toolchest-fsx-databases/tests/",
        remote_database_primary_name="custom_diamond_blastp_db",
        output_path=output_dir_path,
        output_primary_name=output_file_name,
    )

    assert hash.unordered(output_file_path) == 563371739



@pytest.mark.integration
def test_diamond_blastx_standard():
    """
    Tests Diamond blastx mode
    """
    test_dir = "temp_test_diamond_blastx_standard"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_name = "sample_output.tsv"
    output_file_path = f"{output_dir_path}/{output_file_name}"

    toolchest.diamond_blastx(
        inputs="s3://toolchest-integration-tests/sample_r1_shortened.fastq",
        output_path=output_dir_path,
        output_primary_name=output_file_name,
    )

    assert hash.unordered(output_file_path) == 883070112


@pytest.mark.integration
def test_diamond_blastx_distributed():
    """
    Tests DIAMOND BLASTX distributed mode
    """
    test_dir = "./temp_test_diamond_blastx_distributed"
    os.makedirs(f"{test_dir}", exist_ok=True)
    input_file_path = f"{test_dir}/combined_seqs_unfiltered.fna"
    output_dir_path = f"./{test_dir}"
    output_file_name = "sample_output.tsv"
    output_file_path = f"{output_dir_path}/{output_file_name}"

    s3.download_integration_test_input(
        s3_file_key="combined_seqs_unfiltered.fna",
        output_file_path=input_file_path,
        is_private=True,
    )

    print(input_file_path)

    toolchest.diamond_blastx(
        inputs=input_file_path,
        output_path=output_dir_path,
        output_primary_name=output_file_name,
        distributed=True,
    )

    assert 1390254000 < os.path.getsize(output_file_path) <= 1390256000

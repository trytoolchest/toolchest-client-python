import os
import pytest

import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_s3_http_input():
    """
    Tests test function with an http input
    """
    test_dir = "temp_test_http"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_file_path = "https://toolchest-public-examples-no-encryption.s3.amazonaws.com/example.fastq"
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/test_output.txt"

    toolchest.test(
        inputs=input_file_path,
        output_path=output_dir_path
    )

    with open(output_file_path, "r") as f:
        assert f.read().strip() == "success"


@pytest.mark.integration
def test_http_input():
    """
    Tests transfer function with an http input
    """
    test_dir = "temp_test_ftp"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/P48754.fasta"

    toolchest.transfer(
        inputs="https://rest.uniprot.org/uniprotkb/P48754.fasta",
        output_path=output_dir_path
    )

    assert os.path.getsize(output_file_path) == 1962


@pytest.mark.integration
def test_ftp_input():
    """
    Tests transfer function with an ftp input
    """
    test_dir = "temp_test_ftp"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/SRR9990000.fastq.gz"

    toolchest.transfer(
        inputs="ftp://ftp.sra.ebi.ac.uk/vol1/fastq//SRR999/000/SRR9990000/SRR9990000.fastq.gz",
        output_path=output_dir_path
    )

    assert os.path.getsize(output_file_path) == 11632985

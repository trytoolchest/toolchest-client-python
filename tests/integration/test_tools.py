import pytest

import hash
import s3
import toolchest_client as toolchest


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

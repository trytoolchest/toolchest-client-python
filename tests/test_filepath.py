import os
import pytest

from tests.util import hash, s3
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_tilde_filepath():
    """
    Tests Kraken 2 against the standard (v1) database
    """
    test_dir = "~/test_tilde_filepath"
    os.makedirs(os.path.expanduser(test_dir), exist_ok=True)
    input_file_path = "~/kraken_input.fasta"
    output_dir_path = f"{test_dir}"
    output_file_path = os.path.expanduser(f"{output_dir_path}/kraken2_output.txt")

    s3.download_integration_test_input(
        s3_file_key="synthetic_bacteroides_reads.fasta",
        output_file_path=os.path.expanduser(input_file_path),
    )

    toolchest_output = toolchest.kraken2(
        inputs=input_file_path,  # contains tilde
        output_path=output_dir_path,  # contains tilde
    )

    assert hash.unordered(output_file_path) == 886254946

    manual_download_dir_path = f"{test_dir}/manual_download"
    manual_download_file_path = os.path.expanduser(f"{manual_download_dir_path}/kraken2_output.txt")
    toolchest.download(
        manual_download_dir_path,  # contains tilde
        run_id=toolchest_output.run_id
    )

    assert hash.unordered(manual_download_file_path) == 886254946

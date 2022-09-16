import os
import pytest
import time

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_async_execution():
    """
    Tests Kraken 2 running async using a small reference database
    """

    test_dir = "temp_test_async_execution"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/kraken2_output.txt"

    custom_db = "s3://toolchest-fsx-databases/kraken2/k2_viral_20210517/"
    toolchest_run = toolchest.kraken2(
        read_one="s3://toolchest-integration-tests/synthetic_bacteroides_reads.fasta",
        remote_database_path=custom_db,
        output_path=output_dir_path,
        is_async=True,
    )

    run_status = ''
    while run_status != toolchest.Status.READY_TO_TRANSFER_TO_CLIENT:
        time.sleep(5)

        run_status = toolchest.get_status(run_id=toolchest_run.run_id)
        if run_status == toolchest.Status.FAILED:
            print("Toolchest run failed.")

    toolchest.download(
        output_path=output_dir_path,
        run_id=toolchest_run.run_id,
    )

    assert hash.unordered(output_file_path) == 1003212151

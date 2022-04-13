import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration2
def test_rapsearch():
    """
    Tests rapsearch2 on SeqScreen DB
    """

    test_dir = "./test_rapsearch"
    os.makedirs(f"{test_dir}", exist_ok=True)
    output_file_path_aln = f"./{test_dir}/rapsearch2.aln"
    output_file_path_m8 = f"./{test_dir}/rapsearch2.m8"

    toolchest.rapsearch(
        tool_args="-e 1e-9",
        inputs="s3://toolchest-integration-tests/example.fastq",
        output_path=f"{test_dir}/rapsearch2",
    )

    hash.unordered(output_file_path_m8)
    hash.unordered(output_file_path_aln)

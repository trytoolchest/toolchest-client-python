import os
import pytest

from tests.util import hash
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_rapsearch2():
    """
    Tests rapsearch2 on SeqScreen DB
    """

    test_dir = "./temp_test_rapsearch2"
    os.makedirs(f"{test_dir}", exist_ok=True)
    output_file_path_aln = f"./{test_dir}/rapsearch2.aln"
    output_file_path_m8 = f"./{test_dir}/rapsearch2.m8"

    toolchest.rapsearch2(
        tool_args="-e 1e-9",
        inputs="s3://toolchest-integration-tests/example.fastq",
        output_path=f"{test_dir}/",
        output_primary_name="rapsearch2",
    )

    # m8 output is nondeterministic, so we check file size
    assert 71362000 <= os.path.getsize(output_file_path_m8) <= 71362200

    assert 321661100 <= os.path.getsize(output_file_path_aln) <= 321661300
    assert hash.unordered(output_file_path_aln) == 2129168459

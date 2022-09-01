import os
import pytest
os.environ["TOOLCHEST_API_URL"] = "https://toolchest.outputbio.com"
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_salmon_hg38():
    """
    Tests salmon with a scRNA-Seq FASTA file

    """

    test_dir = "temp_test_salmon_hg38"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"

    toolchest.salmon(
        single_end="/Users/noahlebovic/code/toolchest-client-python/small_salmon.fastq",
        output_path=output_dir_path,
        database_name="salmon_hg38",
        database_version=1,
    )

    # Non-deterministic
    assert 8143860 <= os.path.getsize(os.path.join(output_dir_path, "quant.sf")) <= 8143880

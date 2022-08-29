import os
import pytest

from tests.util import hash
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
        single_end="s3://toolchest-integration-tests/salmon/SRR2557119_500k.fastq",
        output_path=output_dir_path,
        database_name="salmon_hg38",
        database_version=1,
    )

    # Non-deterministic – move to different hash or to size
    assert hash.unordered(os.path.join(output_dir_path, "quant.sf")) == 1516704631

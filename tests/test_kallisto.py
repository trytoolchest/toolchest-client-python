import os
import pytest

import toolchest_client as toolchest
from tests.util import hash

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_kallisto_homo_sapiens():
    """
    Tests kallisto with a scRNA-Seq FASTA file

    """

    test_dir = "temp_test_kallisto_hg38"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"

    toolchest.kallisto(
        inputs="s3://toolchest-integration-tests/salmon/SRR2557119_500k.fastq",
        output_path=output_dir_path,
        tool_args="--single -l 150 -s 20",
    )

    assert hash.unordered(os.path.join(output_dir_path, "abundance.tsv")) == 810475052
    assert os.path.getsize(os.path.join(output_dir_path, "abundance.h5")) == 1784377

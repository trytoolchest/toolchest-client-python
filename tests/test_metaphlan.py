import os
import pytest

from tests.util import hash, filter_output
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_metaphlan():
    """
    Tests MetaPhlAn with a fastq file

    """

    test_dir = "temp_test_metaphlan"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    toolchest.metaphlan(
        inputs="s3://toolchest-integration-tests/metaphlan/SRS014464-Anterior_nares.fasta.gz",
        output_path=output_dir_path
    )

    # MetaPhLan includes the command in the output but that contains a non-deterministic uuid so that line is removed.
    filter_output.filter_regex(
        unfiltered_path="/Users/justinherr/temp/test/metaphlan/out.txt",
        filtered_path="/Users/justinherr/temp/test/metaphlan/out_filtered.txt",
        search_regex="#/usr/local/bin/metaphlan.*\n",
        replacement_str="",
    )

    assert hash.unordered(os.path.join(test_dir, "out.txt")) == 1401032462
    assert hash.unordered(os.path.join(test_dir, "SRS014464-Anterior_nares.fasta.gz.bowtie2out.txt")) == 1308716263

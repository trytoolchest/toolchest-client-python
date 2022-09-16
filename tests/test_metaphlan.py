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
    filtered_output_path = os.path.join(output_dir_path, "out_filtered.txt")
    filter_output.filter_regex(
        unfiltered_path=f"{output_dir_path}/out.txt",
        filtered_path=filtered_output_path,
        search_regex="#/usr/local/bin/metaphlan.*\n",
        replacement_str="",
    )
    assert hash.unordered(filtered_output_path) == 1401032462

    bowtie2outfile_path = os.path.join(output_dir_path, "SRS014464-Anterior_nares.fasta.gz.bowtie2out.txt")
    assert hash.unordered(bowtie2outfile_path) == 1308716263

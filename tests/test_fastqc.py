import os
import pytest

from tests.util import hash, filter_output
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_fastqc():
    """
    Tests FastQC with a fastq file

    """

    test_dir = "temp_test_fastqc"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    output_dir_path = f"./{test_dir}"
    filtered_html_output_path = f"{output_dir_path}/sample_r1_shortened_fastqc_filtered.html"
    toolchest.fastqc(
        inputs="s3://toolchest-integration-tests/sample_r1_shortened.fastq",
        output_path=output_dir_path
    )

    filter_output.filter_regex(
        os.path.join(test_dir, "sample_r1_shortened_fastqc.html"),
        filtered_html_output_path,
        search_regex='id="header_filename">([\\w\\s]+)<br',
        replacement_str='id="header_filename"><br'
    )
    assert hash.unordered(filtered_html_output_path) == 816103024
    assert 325000 <= os.path.getsize(os.path.join(test_dir, "sample_r1_shortened_fastqc.zip")) <= 327000

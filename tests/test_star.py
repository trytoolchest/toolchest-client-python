import os
import pytest

from tests.util import s3, hash, filter_output
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_star_grch38():
    """
    Tests STAR against the grch38 database
    """
    test_dir = "temp_test_star_grch38"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_file_path = "./small_star.fastq"
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/Aligned.out.sam"
    filtered_output_file_path = f"{output_dir_path}/Aligned.filtered.out.sam"

    s3.download_integration_test_input(
        s3_file_key="small_star_500k.fastq",
        output_file_path=input_file_path,
        is_private=True,
    )

    toolchest.STAR(
        read_one=input_file_path,
        output_path=output_dir_path,
        database_name="GRCh38",
    )

    # Because STAR output contains run ID (non-deterministic), verify that the number of bytes is in range
    assert 185952700 <= os.path.getsize(output_file_path) <= 185952900  # expected size 185952796

    # Filter non-deterministic metadata lines
    filter_output.filter_sam(output_file_path, filtered_output_file_path)
    assert hash.unordered(filtered_output_file_path) == 2099424598


@pytest.mark.integration
@pytest.mark.skip(reason="Pysam removed so parallelization is disabled until a new sam file merger is written or found")
def test_star_grch38_parallel():
    """
    Tests STAR against the grch38 database, using parallel mode
    """
    test_dir = "temp_test_star_grch38_parallel"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_file_path = "./large_star.fastq"
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/Aligned.out.sam"

    s3.download_integration_test_input(
        s3_file_key="large_star_15GB.fastq",
        output_file_path=input_file_path,
        is_private=True,
    )

    toolchest.STAR(
        read_one=input_file_path,
        output_path=output_file_path,
        database_name="GRCh38",
        parallelize=True,
    )

    # Because STAR output contains run ID (non-deterministic), verify that the number of bytes is in range
    # TODO: verify new file size with dockerized STAR after re-enabling parallelization
    # TODO: add a hash test of output file without @PG and @CO lines
    assert 33292990718 <= os.path.getsize(output_file_path) <= 33292994718


@pytest.mark.integration
def test_star_grch38_dangerous_arg():
    """
    Tests STAR against the grch38 database, with a dangerous arg (changing functionality)
    """
    test_dir = "temp_test_star_grch38"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_file_path = "./small_star.fastq"
    output_dir_path = f"./{test_dir}"
    output_file_path = f"{output_dir_path}/Aligned.out.bam"

    s3.download_integration_test_input(
        s3_file_key="small_star_500k.fastq",
        output_file_path=input_file_path,
        is_private=True,
    )

    toolchest.STAR(
        read_one=input_file_path,
        output_path=output_dir_path,
        database_name="GRCh38",
        tool_args="--outSAMtype BAM Unsorted",
        parallelize=True,  # this should be deliberately ignored
    )

    # Because STAR output contains run ID (non-deterministic) and BAMs are compressed,
    # verify that the number of bytes is in range
    assert 38236000 <= os.path.getsize(output_file_path) <= 38236100  # expected size 38236044

    # Make sure all non-parallel files exist as well
    assert os.path.isfile(f"{output_dir_path}/Log.final.out")
    assert os.path.isfile(f"{output_dir_path}/Log.out")
    assert os.path.isfile(f"{output_dir_path}/Log.progress.out")
    assert os.path.isfile(f"{output_dir_path}/SJ.out.tab")

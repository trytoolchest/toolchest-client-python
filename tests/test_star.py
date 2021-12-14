import os
import pytest

from tests.util import s3
import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_star_grch38():
    """
    Tests STAR against the grch38 database
    """
    test_dir = "test_star_grch38"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_file_path = "./small_star.fastq"
    output_dir_path = f"./{test_dir}/"
    output_file_path = f"{output_dir_path}Aligned.out.sam"

    s3.download_integration_test_input(
        s3_file_key="small_star_500k.fastq",
        output_file_path=input_file_path,
    )

    toolchest.STAR(
        read_one=input_file_path,
        output_path=output_file_path,
        database_name="GRCh38",
    )

    # Because STAR is non-deterministic, verify that the number of bytes is in range
    assert 185952744 <= os.path.getsize(output_file_path) <= 185952766


@pytest.mark.integration
def test_star_grch38_parallel():
    """
    Tests STAR against the grch38 database, using parallel mode
    """
    test_dir = "test_star_grch38_parallel"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_file_path = "./large_star.fastq"
    output_dir_path = f"./{test_dir}/"
    output_file_path = f"{output_dir_path}Aligned.out.sam"

    s3.download_integration_test_input(
        s3_file_key="large_star_15GB.fastq",
        output_file_path=input_file_path,
    )

    toolchest.STAR(
        read_one=input_file_path,
        output_path=output_file_path,
        database_name="GRCh38",
    )

    # Because STAR is non-deterministic, verify that the number of bytes is in range
    assert 33292992706 <= os.path.getsize(output_file_path) <= 33292992730


@pytest.mark.dev
def test_star_grch38_dangerous_arg():
    """
    Tests STAR against the grch38 database, with a dangerous arg (changing functionality)
    """
    test_dir = "test_star_grch38"
    os.makedirs(f"./{test_dir}", exist_ok=True)
    input_file_path = "./small_star.fastq"
    output_dir_path = f"./{test_dir}/"
    output_file_path = f"{output_dir_path}Aligned.out.bam"

    s3.download_integration_test_input(
        s3_file_key="small_star_500k.fastq",
        output_file_path=input_file_path,
    )

    toolchest.STAR(
        read_one=input_file_path,
        output_path=output_dir_path,
        database_name="GRCh38",
        tool_args="--outSAMtype BAM Unsorted",
    )

    # Because STAR is non-deterministic and BAMs are are compressed verify that the number of bytes matches
    assert os.path.getsize(output_file_path) == 38236026

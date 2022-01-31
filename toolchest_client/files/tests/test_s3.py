import pytest

from .. import assert_accessible_s3, get_s3_file_size, get_params_from_s3_uri
from ...api.exceptions import ToolchestS3AccessError

EXAMPLE_FASTQ_SIZE = 48468258
EXAMPLE_FASTQ_URI = "s3://toolchest-public-examples/example.fastq"


def test_s3_params():
    example_s3_uri = "s3://toolchest-public-examples/dummy-id/example.fastq"
    params = get_params_from_s3_uri(example_s3_uri)
    target_params = {
        "arn": "arn:aws:s3:::toolchest-public-examples/dummy-id/example.fastq",
        "bucket": "toolchest-public-examples",
        "key": "dummy-id/example.fastq",
        "key_initial": "dummy-id",
        "key_final": "example.fastq"
    }

    assert params == target_params


@pytest.mark.integration
def test_public_s3_file():
    assert_accessible_s3(EXAMPLE_FASTQ_URI)


@pytest.mark.integration
def test_fake_s3_file():
    fake_s3_uri = "s3://toolchest-this-is-a-bad-bucket/bogus.fastq"
    with pytest.raises(ToolchestS3AccessError):
        assert_accessible_s3(fake_s3_uri)


@pytest.mark.integration
def test_s3_file_size():
    assert get_s3_file_size(EXAMPLE_FASTQ_URI) == EXAMPLE_FASTQ_SIZE

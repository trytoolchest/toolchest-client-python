import pytest

from .. import assert_accessible_s3, get_params_from_s3_uri


def test_s3_params():
    example_s3_uri = "s3://toolchest-public-examples/example.fastq"
    params = get_params_from_s3_uri(example_s3_uri)
    target_params = {
        "arn": "arn:aws:s3:::toolchest-public-examples/example.fastq",
        "bucket": "toolchest-public-examples",
        "key": "example.fastq"
    }

    assert params == target_params


@pytest.mark.integration
def test_public_s3_file():
    public_s3_uri = "s3://toolchest-public-examples/example.fastq"
    with pytest.raises(ValueError):
        assert_accessible_s3(public_s3_uri)

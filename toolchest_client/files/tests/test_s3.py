from .. import get_params_from_s3_uri


def test_s3_params():
    example_s3_uri = "s3://toolchest-public-examples/example.fastq"
    params = get_params_from_s3_uri(example_s3_uri)
    target_params = {
        "arn": "arn:aws:s3:::toolchest-public-examples/example.fastq",
        "bucket": "toolchest-public-examples",
        "key": "example.fastq"
    }

    assert params == target_params

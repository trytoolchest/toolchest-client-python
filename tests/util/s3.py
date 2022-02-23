import boto3
from botocore.exceptions import ClientError


# Downloads input from S3 to local file path.
# Used for tests that upload local inputs.
def download_integration_test_input(s3_file_key, output_file_path, is_private=False):
    s3_client = boto3.client('s3')
    bucket_name = 'toolchest-integration-tests-private' if is_private else 'toolchest-integration-tests'
    s3_client.download_file(bucket_name, s3_file_key, output_file_path)

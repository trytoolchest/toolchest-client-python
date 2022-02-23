import boto3
from botocore.exceptions import ClientError


# Downloads input from S3 to local file path.
# Used for tests that upload local inputs.
def download_integration_test_input(s3_file_key, output_file_path):
    s3_client = boto3.client('s3')
    try:
        s3_client.download_file('toolchest-integration-tests', s3_file_key, output_file_path)
    except ClientError:
        try:
            s3_client.download_file('toolchest-integration-tests-private', s3_file_key, output_file_path)
        except ClientError as err:
            raise err

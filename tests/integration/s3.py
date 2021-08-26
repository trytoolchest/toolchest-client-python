import boto3


# todo: once able to pass S3 paths as input, remove this ability
def download_integration_test_input(s3_file_key, output_file_path):
    s3 = boto3.client('s3')
    s3.download_file('toolchest-integration-tests', s3_file_key, output_file_path)

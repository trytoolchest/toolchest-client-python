# Using AWS with Toolchest

Toolchest supports reading and writing from your S3 buckets. You can also run Toolchest within your own AWS account, so the files you pass to `inputs` and `output_path` aren't transferred outside your account.

## Input Files

Files stored on S3 can be passed in as inputs, using the file's S3 URI.  For example:
s
```python
tc.kraken2(
    inputs="s3://toolchest-demo-data/SRR16201572_R1.fastq",
    output_path="./",
)
```

## Output to S3

Some tools support uploading outputs directly to your custom S3 bucket. For these runs, put the S3 bucket + prefix in 
**`output_path`**. For example:

```python
tc.kraken2(
    inputs="./example.fastq",
    output_path="s3://your-output/your-intended-subfolder",
)
```

## Custom Databases

For some tools, you can use use a custom database stored on S3 using **`custom_database_path`**:

```python
tc.kraken2(
    inputs="./example.fastq",
    output_path="./example_output_dir",
  	custom_database_path="s3://your-databases/your-kraken2-database",
)
```

Toolchest needs permission to list and copy all of the files in the S3 prefix you use.

## Granting Permissions to Toolchest to Access Your S3 Bucket

To grant Toolchest access to your S3 bucket, use this policy:

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "Toolchest",
			"Effect": "Allow",
			"Principal": {
				"AWS": "arn:aws:iam::172533437917:role/toolchest-worker-node-role"
			},
			"Action": [
				"s3:GetObject",
				"s3:ListBucket"
			],
			"Resource": [
				"arn:aws:s3:::YOUR_BUCKET_NAME",
				"arn:aws:s3:::YOUR_BUCKET_NAME/*"
			]
		}
	]
}
```

(Make sure to replace`YOUR_BUCKET_NAME` with your bucket)

You can restrict this to specific files or prefixes with whatever IAM policy you'd like, just make sure that Toolchest 
has `s3:GetObject` for any file you'll use with Toolchest and `s3:ListBucket` permissions for any prefix.

After you add this policy, let us know and we'll complete the setup process!

## Running Toolchest in Your Own AWS Account

You can run Toolchest in your own AWS account, and the data that you pass to `inputs` and `output_path` doesn't leave 
your own AWS environment. [Get in touch with us](mailto:hello@trytoolchest.com) if you'd like to know more!
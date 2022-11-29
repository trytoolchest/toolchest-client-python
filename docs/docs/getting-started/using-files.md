# Using Files

Toolchest works with files on your computer (local files) or files on something like S3 (remote files). We recommend 
using local or S3 files for data integrity and speed of execution, but HTTP or FTP URLs are supported too.

For all tools and file types, `inputs` takes a string path or a list of paths. `output_path` always takes a directory 
path.

Let's take a look at what it looks like to use different types of local and remote paths!

!!! note "You can mix and match file sources"
    You can mix and match local and remote files in the same call. Every file is handled independently, so you can use S3, 
    FTP, and local files together.

## Local files and directories

Local files are the most intuitive: you just pass normal paths directly to Toolchest. In the background, the files are 
transferred to and from the cloud.

`inputs` takes file and/or directory path(s).

`output_path` takes a path to a directory. Output files are written in this directory.

### Local directory inputs
If a directory is passed, all files within the directory are used as input. Directory structure will be destroyed unless
`compress_inputs=True` is provided as an argument.

For example if you have the following directory structure:
```text
/path/to/base/directory/
    subdirectory_one/
        input.fastq
    subdirectory_two/
        input.fastq
        info.txt
```
and you used the following toolchest call:
```python
tc.test(
    inputs="/path/to/base/directory/",
    compress_inputs=True
)
```
Then the input files will retain the directory structure without name conflicts. If `compress_inputs` is set to `False`
or not provided, the 2 `inputs.fastq` would overwrite whichever one was downloaded second. 

## Remote files

### AWS S3

S3 files are the fastest and most reliable input source. Toolchest pulls directly from the path you pass.

- `inputs` takes S3 URIs for a file. If you have multiple files in an S3 directory, make sure to list the directory first 
and pass each file as an input.
- `output_path` accepts an S3 URI for a S3 prefix.

Here's an example using the `test` package with an S3 input:
```python
tc.test(
    inputs="s3://toolchest-public-examples/example.fastq",
    output_path="s3://toolchest-public-output/remote-output/"
)
```

!!! note "Make sure Toolchest has access to your S3 bucket"

    To grant Toolchest access, see [AWS Integration](../feature-reference/using-aws-with-toolchest.md).

### HTTP/HTTPS

!!! warning "HTTP and HTTPS files are dangerous!"
    We can't guarantee data integrity on transfer, because different servers behave differently. Make sure that the HTTP 
    server supports `GET` requests with the `range` header. Always use a local or S3 file path if possible. Ye be warned!

- `inputs` takes an HTTP URL for a file. If you have multiple files in an HTTP directory, make sure to list the directory 
first, and pass each file as an input.
- `output_path` does not accept HTTP outputs at this time.

Here's an example using the `test` package with an HTTP input:
```python
tc.test(
    inputs="https://rest.uniprot.org/uniprotkb/P48754.fasta",
    output_path="./"
)
```

### FTP

!!! warning "FTP files are dangerous!"
    We can't guarantee data integrity on transfer, because different servers behave differently. Always use a local or S3 
    file path if possible. Ye be warned!

- `inputs` accepts an FTP URL for a file. If you have multiple files in an FTP directory, make sure to list the 
directory first, and pass each file as an input.
- `output_path` does not accept FTP outputs at this time.

Here's an example using the `test` package with an FTP input:
```python
tc.test(
    inputs="ftp://ftp.sra.ebi.ac.uk/vol1/fastq//SRR999/000/SRR9990000/SRR9990000.fastq.gz",
    output_path="./"
)
```
# Toolchest-wrapped Command-line Software

Note: if you haven't already, make sure you [have an API key](https://trytoolchest.com) and Toolchest is installed!

The most popular bioinformatics software is run through the command line. Toolchest wraps this software in Python and 
runs it on the cloud.

## A quick start

To get started, we'll use STAR, but you can use any of the [packages supported by Toolchest](../tool-reference/about.md)
. On the command-line, running STAR looks like:

```shell
STAR --outFileNamePrefix ./output_path --genomeDir ./database_CRCh38 --readFilesIn ./inputs/
```

With Toolchest, it's:

```python
import toolchest-client as tc

tc.set_key("YOUR_KEY")

tc.STAR(
    inputs="s3://toolchest-demo-data/SRR2557119_small.fastq",
    output_path="./output_path/",
    database_name="GRCh38",
)
```

and it runs in the cloud! Breaking down the arguments:

- `inputs` are your input files. They can be on your computer, or somewhere else like S3.
- `output_path` is where your output files are written. This can also be your computer, or somewhere else like S3.
- `database_name` is the name of the Toolchest-hosted database.

## Adding more options

```python
import toolchest-client as tc

tc.set_key("YOUR_KEY")

tc.STAR(
    inputs="s3://toolchest-demo-data/SRR2557119_small.fastq",
    output_path="./output/",
    database_name="GRCh38",
    database_version="1",
    tool_args="--outSAMtype BAM Unsorted"
)
```

We added two new arguments:
- `database_version` is the version number of the Toolchest-hosted database.
- `tool_args` are the arguments that you would normally set on the command-line to customize execution.

Next, let's learn more about what kinds of files you can use with Toolchest.

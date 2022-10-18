**FastQC** is a quality control tool for genomic sequence data. [See their website for more details](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/).

# Function Call

```python
tc.fastqc(
    inputs,
    output_path=None,
    contaminants=None,
    adapters=None,
    limits=None,
    tool_args="",
    is_async=False,
)
```

## Function Arguments


| Argument               | Use in place of:                    | Description                                                                                                                                                                                                               |
|:-----------------------|:------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `inputs`               | input file location                 | Path to one or more files to use as input.  \nSAM, BAM, or FASTQ formats are supported, as well as gzip-compressed variants. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md). |
| `output_path`          | `-o` (directory name)               | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                        |
| `contaminants`         | `-c` or `--contaminants` file path. | (optional) Path to a custom contaminants file.                                                                                                                                                                            |
| `adapters`             | `-a` or `--adapters` file path.     | (optional) Path to a custom adapters file.                                                                                                                                                                                |
| `limits`               | `-l` or `--limits` file path        | (optional) Path to a custom limits file.                                                                                                                                                                                  |
| `tool_args`            | all other arguments                 | (optional) Additional arguments to be passed to FastQC. This should be a string of arguments like the command line.                                                                                                       |
| `is_async`             |                                     | Whether to run a job asynchronously.  See [Async Runs](../../feature-reference/async-runs.md) for more.                                                                                                                   |



## Output Files

A FastQC run will output the html report and output zip into `output_path`:

- `{input file name}_fastqc.html`: FastQC HTML report for checking data quality
- `{input file name}\_fastqc.zip`: Zip directory containing the HTML report and some supporting files

# Tool Versions

Toolchest currently supports version **0.11.9** of FastQC.
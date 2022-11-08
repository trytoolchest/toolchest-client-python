**DIAMOND BLASTX** is [DIAMOND](../diamond.md)'s mode for translated DNA sequence searches. For more information, see the tool's [GitHub repo and wiki](https://github.com/bbuchfink/diamond).

# Function Call

```python
tc.diamond_blastx(
  	inputs,
  	output_path=None,
    database_name="diamond_blastx_standard",
  	database_version="1",
  	remote_database_path=None,
    remote_database_primary_name=None,
  	tool_args="",
  	is_async=False,
)
```

## Function Arguments

See the Notes section below for more details.

| Argument                       | Use in place of:    | Description                                                                                                                                                                                                                    |
| :----------------------------- | :------------------ |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `inputs`                       | `-q`, `--query`     | Path to one or more files to use as input. FASTA or FASTQ formats are supported, as well as gzip-compressed FASTA/FASTQ files. The files can be a local or remote, see [Using Files](../../../getting-started/using-files.md). |
| `output_path`                  | `-o`, `--out`       | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be a local or remote, see [Using Files](../../../getting-started/using-files.md).                          |
| `database_name`                | `-d`                | (optional) Name of database to use for DIAMOND BLASTX. Defaults to `"diamond_blastx_standard"`, the SeqScreen database.                                                                                                        |
| `database_version`             | database version    | (optional) Version of database to use for DIAMOND BLASTX. Defaults to `"1"`.                                                                                                                                                   |
| `remote_database_path`         | `-d` (path)         | (optional) AWS S3 URI to the directory that contains your custom database.                                                                                                                                                     |
| `remote_database_primary_name` | `-d` (name)         | (optional) The primary name (e.g. UNIREF100.mini) of your custom database.                                                                                                                                                     |
| `tool_args`                    | all other arguments | (optional) Additional arguments to be passed to Diamond BLASTX. This should be a string of arguments like the command line.                                                                                                    |
| `is_async`                     |                     | Whether to run a job asynchronously.  See [Async Runs](../../../feature-reference/async-runs.md) for more.                                                                                                                     |

DIAMOND BLASTX runs are aligned against the SeqScreen database by default. See the [Databases](#databases) section for more details.

# Tool Versions

Toolchest currently supports version **2.0.14** of DIAMOND. Every request to run DIAMOND BLASTX with Toolchest will default to this version.

# Databases

Toolchest currently supports the following databases for DIAMOND BLASTX:

| `database_name`           | `database_version` | Description                                                                                                                                                |
| :------------------------ | :----------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `diamond_blastx_standard` | `1`                | SeqScreen DIAMOND BLASTX Database. See [the SeqScreen wiki](https://gitlab.com/treangenlab/seqscreen/-/wikis/02.-SeqScreen-Dependencies) for more details. |

# Supported Additional Arguments

- `-e`
- `--evalue`
- `-f`
- `-l`
- `--masking`
- `--min-orf`
- `--no-self-hits`
- `--outfmt`
- `--sallseqid`
- `--salltitles`
- `--strand`
- `--top`
- `--unal`

Additional arguments can be specified under the `tool_args` argument.
**Salmon** is a computational genomics tool for transcriptomic analysis. For more information, see the tool's 
[GitHub repo](https://github.com/COMBINE-lab/salmon). Toolchest only supports running `salmon quant` with pre-built 
indexes in mapping mode at this time.

# Function Call

```python
tc.salmon(
  	read_one=None,
  	read_two=None,
    single_end=None,
  	output_path=None,
  	tool_args="",
  	database_name="salmon_hg38",
  	database_version="1",
    library_type="A",
  	is_async=False,
)
```

## Function Arguments

| Argument           | Use in place of:     | Description                                                                                                                                                                                                                |
| :----------------- | :------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `read_one`         | `-1`                 | (optional) Path or list of paths to R1 of paired-end read input files. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                |
| `read_two`         | `-2`                 | (optional) Path or list of paths to R2 of paired-end read input files. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                |
| `single_end`       | `-r`                 | (optional) Path or list of paths to of single-end (or just R1 or R2) read input files. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                |
| `output_path`      | output file location | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md). |
| `tool_args`        | all other arguments  | (optional) Additional arguments to be passed to Salmon. This should be a string of arguments like the command line.                                                                                                        |
| `database_name`    | `-i`                 | (optional) Name of database to use for Kraken 2 alignment. Defaults to `"salmon_hg38"`.                                                                                                                                    |
| `database_version` | `-i`                 | (optional) Version of database to use for Kraken 2 alignment. Defaults to `"1"`.                                                                                                                                           |
| `library_type`     | `-l`, `--libType`    | (optional) The library type used. Defaults to "A" for automatic classification. See [the Salmon docs on library types](https://salmon.readthedocs.io/en/latest/salmon.html#what-s-this-libtype) for more.                  |
| `is_async`         |                      | Whether to run a job asynchronously.  See [Async Runs](../../feature-reference/async-runs.md) for more.                                                                                                                                    |

See the [Databases](#databases) section for more details.

## Notes

### Paired-end inputs

Paired-end read inputs can be set with either `inputs` or through `read_one` and `read_two`.

Make sure that the first item in `read_one` corresponds to the first item in `read_two`– and so on.

If you only have one end of a paired-end run, use the `single_end` argument.

# Tool Versions

Toolchest currently supports version **1.9.0** of Salmon.

# Databases

Toolchest currently supports the following databases for Salmon:

| `database_name` | `database_version` | Description                                                                      |
| :-------------- | :----------------- | :------------------------------------------------------------------------------- |
| `hg38`          | `1`                | hg38 precomputed index for Salmon, pulled from <http://refgenomes.databio.org/>. |

# Other modes

Only `quant` mode is supported at this time.
**RAPSearch2** is an aligner for protein similarity searches. It aligns DNA reads or protein sequences against a 
protein database. For more information, see the tool's [homepage](https://omics.informatics.indiana.edu/mg/RAPSearch2/)
, [GitHub repo](https://github.com/zhaoyanswill/RAPSearch2), and [Sourceforge page](http://rapsearch2.sourceforge.net/).

Function Call
=============

```python
tc.rapsearch2(
    inputs,
    output_path=None,
    database_name="rapsearch2_seqscreen",
    database_version="1",
    tool_args="",
    is_async=False,
)
```

Function Arguments
------------------

See the Notes section below for more details.

| Argument           | Use in place of:    | Description                                                                                                                                                                                                                                                   |
| :----------------- | :------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `inputs`           | `-q`                | Path to one or more files to use as input. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                                                                               |
| `output_path`      | `-o`                | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                    |
| `database_name`    | `-d`\*              | (optional) Name of database to use for RAPSearch2 alignment. Defaults to `"GRCh38"` (human genome).                                                                                                                                                           |
| `database_version` | `-d`\*              | (optional) Version of database to use for RAPSearch2 alignment. Defaults to `"1"`.                                                                                                                                                                            |
| `tool_args`        | all other arguments | (optional) Additional arguments to be passed to RAPSearch2. This should be a string of arguments like the command line. See [Supported Additional Arguments](https://docs.trytoolchest.com/docs/rapsearch-2#supported-additional-arguments) for more details. |
| `is_async`         |                     | Whether to run a job asynchronously.  See [Async Runs](../../feature-reference/async-runs.md) for more.                                                                                                                                                                       |

\*See the [Databases](#databases) section for more details.

Tool Versions
=============

Toolchest currently supports version **2.24** of RAPSearch2.

Databases
=========

Toolchest currently supports the following databases for RAPSearch2:

| `database_name`       | `database_version` | Description                                                                                                                                            |
| :-------------------- | :----------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `rapsearch_seqscreen` | `1`                | SeqScreen RAPSearch2 Database. See [the SeqScreen wiki](https://gitlab.com/treangenlab/seqscreen/-/wikis/02.-SeqScreen-Dependencies) for more details. |

Supported Additional Arguments
==============================

- `-a`
- `-b`
- `-e`
- `-g`
- `-i`
- `-l`
- `-p`
- `-s`
- `-t`
- `-v`
- `-w`
- `-x`

Additional arguments can be specified under the `tool_args` argument.
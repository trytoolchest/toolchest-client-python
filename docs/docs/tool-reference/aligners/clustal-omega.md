**Clustal Omega** is a fast and scalable tool that makes multiple sequence alignments of protein sequences. For more 
information, see the tool's [homepage](http://www.clustal.org/omega/).

Function Call
=============

```python
tc.clustalo(
    inputs,
    output_path=None,
    tool_args="",
    is_async=False,
)
```

Function Arguments
------------------

See the Notes section below for more details.

| Argument      | Use in place of:    | Description                                                                                                                                                                                                                                                        |
| :------------ | :------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inputs`      | `-i`                | Path to one or more files to use as input. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                                                                                    |
| `output_path` | `-o`                | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                         |
| `tool_args`   | all other arguments | (optional) Additional arguments to be passed to Clustal Omega. This should be a string of arguments like the command line. See [Supported Additional Arguments](#supported-additional-arguments) for more details. |
| `is_async`    |                     | Whether to run a job asynchronously.  See [Async Runs](../../feature-reference/async-runs.md) for more.                                                                                                                                                                            |

Tool Versions
=============

Toolchest currently supports version **1.2.4** of Clustal Omega.

Supported Additional Arguments
==============================

- `--auto`
- `--dealign`
- `--infmt`
- `--is-profile`
- `--iter`
- `--iterations`
- `--max-guidetree-iterations`
- `--max-hmm-iterations`
- `--maxnumseq`
- `--maxseqlen`
- `--outfmt`
- `--output-order`
- `--residuenumber`
- `--resno`
- `--seqtype`
- `-t`
- `--wrap`

Additional arguments can be specified under the `tool_args` argument.
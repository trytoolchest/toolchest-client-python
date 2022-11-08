**MEGAHIT** is an assembler that's optimized for metagenomes. For more information, see the tool's 
[GitHub repo and wiki](https://github.com/voutcn/megahit).

Function Call
=============

```python
tc.megahit(
  	read_one=None,
  	read_two=None,
  	interleaved=None,
    single_end=None,
  	output_path=None,
  	tool_args="",
  	is_async=False,
)
```

Function Arguments
------------------

See the Notes section below for more details.

| Argument      | Use in place of:    | Description                                                                                                                                                                                        |
| :------------ | :------------------ |:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `read_one`    | `-1`                | (optional) Path to R1 of paired-end short read input files. The file can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                            |
| `read_two`    | `-2`                | (optional) Path to R2 of paired-end short read input files. The file can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                            |
| `interleaved` | `--12`              | (optional) Path to the file containing interleaved reads. The file can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                              |
| `single_end`  | `-r`                | (optional) Path to the file containing singled-ended reads. The file can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                            |
| `output_path` | `-o`                | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md). |
| `tool_args`   | all other arguments | (optional) A string containing additional arguments to be passed to MEGAHIT, formatted as if using the command line.                                                                               |
| `is_async`    |                     | Whether to run a job asynchronously. See [Async Runs](../../feature-reference/async-runs.md) for more.                                                                                             |

Notes
-----

### Paired-end reads

For each paired-end input, make sure the corresponding read is in the same position in the input list. For example, two 
pairs of paired-end files – `one_R1.fastq`, `one_R2.fastq`, `two_R1.fastq`, `two_R2.fastq` – should be passed to 
Toolchest as:

```python
tc.megahit(
  read_one=["one_R1.fastq", "two_R1.fastq"],
  read_two=["one_R2.fastq", "two_R2.fastq"],
  ...
)
```

Tool Versions
=============

Toolchest currently supports version **1.2.9** of MEGAHIT. 

Supported Additional Arguments
==============================

- \--min-count
- \--k-list
- \--k-min
- \--k-max
- \--k-step
- \--no-mercy
- \--bubble-level
- \--merge-level
- \--prune-level
- \--prune-depth
- \--disconnect-ratio
- \--low-local-ratio
- \--max-tip-len
- \--cleaning-rounds
- \--no-local
- \--kmin-1pass
- \--presets
- \--min-contig-len

Set additional arguments with `tool_args`. For example: `tool_args="--no-local --no-mercy"`
**Unicycler** is an assembly pipeline for bacterial genomes. For more information, see the tool's 
[GitHub repo and wiki](https://github.com/rrwick/Unicycler).

Function Call
=============

```python
tc.unicycler(
  	read_one=None,
  	read_two=None,
  	long_reads=None,
  	output_path=None,
  	tool_args="",
  	is_async=False,
)
```

Function Arguments
------------------

| Argument      | Use in place of:    | Description                                                                                                                                                                                                                                                |
| :------------ | :------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `read_one`    | `-1`                | (optional) Path to R1 of paired-end short read input files. The file can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                                                            |
| `read_two`    | `-2`                | (optional) Path to R2 of paired-end short read input files. The file can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                                                            |
| `long_reads`  | `-l`                | (optional) Path to the file containing long reads. The file can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                                                                     |
| `output_path` | `-o`                | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                 |
| `tool_args`   | all other arguments | (optional) Additional arguments to be passed to Unicycler. This should be a string of arguments like the command line. See [Supported Additional Arguments](https://docs.trytoolchest.com/docs/unicycler#supported-additional-arguments) for more details. |
| `is_async`    |                     | Whether to run a job asynchronously.  See [Async Runs](../../feature-reference/async-runs.md) for more.                                                                                                                                                                    |

Notes
-----

### Paired-end reads

Paired-end short read inputs should be specified with both `read_one` and `read_two`.

Tool Versions
=============

Toolchest currently supports version **0.4.9** of Unicycler. 

Supported Additional Arguments
==============================

- `--depth_filter`
- `--kmer_count`
- `--kmers`
- `--largest_component`
- `--linear_seqs`
- `--low_score`
- `--max_kmer_frac`
- `--min_component_size`
- `--min_dead_end_size`
- `--min_fasta_length`
- `--min_kmer_frac`
- `--min_polish_size`
- `--mode`
- `--no_correct`
- `--no_miniasm`
- `--no_pilon`
- `--no_rotate`
- `--scores`
- `--start_gene_cov`
- `--start_gene_id`
- `--verbosity`

Additional arguments can be specified under the `tool_args` argument.
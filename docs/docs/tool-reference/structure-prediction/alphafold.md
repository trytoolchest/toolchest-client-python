AlphaFold is a deep learning tool for predicting a protein’s 3D structure from its amino acid sequence. It was 
developed by DeepMind and utilizes GPU compute. For more information, see the tool's 
[homepage](https://alphafold.ebi.ac.uk/) and [GitHub repo](https://github.com/deepmind/alphafold).

Function Call
=============

```python
tc.alphafold(
  	inputs,
  	output_path=None,
  	model_preset=None,
  	max_template_date=None,
  	use_reduced_dbs=False,
  	is_prokaryote_list=None,
  	is_async=False,
)
```

Function Arguments
------------------

See the Notes section below for more details.

| Argument             | Use in place of:          | Description                                                                                                                                                                                                                   |
| :------------------- | :------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inputs`             | `--fasta-paths`           | Path to one or more files to use as input. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                                               |
| `output_path`        | `--output_dir`            | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).    |
| `model_preset`       | `--model_preset`          | (optional) Specific AlphaFold model to use. Options are [`monomer`, `monomer_casp14`, `monomer_ptm`, `multimer`]. Defaults to `monomer`.                                                                                      |
| `max_template_date`  | `--max_template_date`     | (optional) String of date in YYYY-MM-DD format.  Restricts protein structure prediction to those in the database before this date. Defaults to today's date.                                                                  |
| `use_reduced_dbs`    | `--db_preset=reduced_dbs` | (optional) Whether to use a smaller version of the BFD database. If true, reduces run time at the cost of result quality.                                                                                                     |
| `is_prokaryote_list` | `--is_prokaryote_list`    | (optional) List of booleans that determines whether all input sequences in the given FASTA file are prokaryotic. Expects the string normally used input into AlphaFold (e.g. "true,true" if there are two prokaryote inputs). |
| `is_async`           |                           | Whether to run a job asynchronously.  See [Async Runs](../../feature-reference/async-runs.md) for more.                                                                                                                                       |

Tool Versions
=============

Toolchest currently supports version **2.1.2** of AlphaFold. 

Database
========

Toolchest's implementation of AlphaFold uses AlphaFold's required genetic sequence databases. For a complete list of databases used, see the tool's [GitHub page](https://github.com/deepmind/alphafold).

Supported Additional Arguments
==============================

Toolchest supports the following arguments for AlphaFold: 

- `--db_preset`
- `--is_prokaryote_list`
- `--max_template_date`
- `--model_preset`

However, these should be specified via specific argument values in the function call, rather than through a generic `tool_args` argument (like other Toolchest tools). See [Function Arguments](#function-arguments) for more details.
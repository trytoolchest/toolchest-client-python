**HUMAnN 3** is a workflow tool for profiling microbial pathways in metagenomic and metatranscriptomic data. To learn 
more about the tool, check out its [homepage](http://huttenhower.sph.harvard.edu/humann) and 
[GitHub repo](https://github.com/biobakery/humann).

# Function Call

```python
tc.humann3(
  	inputs,
  	output_path=None,
  	tool_args="",
    taxonomic_profile=None,
    mode=tc.tools.humann3.HUMAnN3Mode.HUMANN,
    input_pathways=None,
    output_primary_name=None,
  	is_async=False,
)
```

## Function Arguments

See the Notes section below for more details.


| Argument                  | Use in place of:          | Description                                                                                                                                                                                                                                                                           |
|:--------------------------|:--------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `inputs`                  | `--input`                 | Path to a _single_ file that will be passed in as input. FASTA and FASTQ formats (gzip compressed or uncompressed) are supported. Uncompressed SAM/BAM and M8 inputs are also supported. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md). |
| `output_path`             | `--output`                | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                                                                    |
| `output_primary_name`     |                           | (optional) (optional) If you're using a mode that produces an individual output file, set the name here.                                                                                                                                                                              |
| `taxonomic_profile`       | `--taxonomic-profile`     | (optional) Path to a MetaPhlAn output tsv (taxonomic profile). Significantly accelerates execution if  provided. See [the HUMAnN 3 docs](https://github.com/biobakery/humann#custom-taxonomic-profile) on the topic for more.                                                         |
| `mode`                    | `humann $MODE`            | (optional) (optional) If you're running a humann3 utility scripts, put it here! Defaults to executing raw `humann`. This is an enum, see the note below this table for more.                                                                                                          |
| `input_pathways`          | `--input-pathways`        | (optional) Path to input pathways from a  `humann` run for use with `humann_unpack_pathways` mode.                                                                                                                                                                                    |
| `tool_args`               | all other arguments       | (optional) Additional arguments to be passed to MetaPhlAn. This should be a string of arguments like the command line.                                                                                                                                                                |
| `is_async`                |                           | Whether to run a job asynchronously.  See [Async Runs](../../feature-reference/async-runs.md) for more.                                                                                                                                                                               |

Note on `mode`: `mode` is an enum, accessible at `tc.tools.humann.HUMAnN3Mode` – e.g. 
`tc.tools.humann.HUMAnN3Mode.RENORM_TABLE`.

# Tool Versions

Toolchest supports version **3.1.1** of HUMAnN.

# Databases

Toolchest currently supports the following databases for HUMAnN:

| `database_name` | `database_version` | Description                                                                                                                                                       |
| :-------------- | :----------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ChocoPhlAn`    | N/A                | The ChocoPhlAn database, provided by the Huttenhower lab. This database is required, and is not user configurable. Used via the `--nucleotide-database` argument. |
| `UniRef90`      | `1`                | The UniRef 90 database. Used via the `--protein-database` argument.                                                                                               |

# Supported Additional Arguments

- \--bypass-nucleotide-index
- \--bypass-nucleotide-search
- \--bypass-prescreen
- \--bypass-translated-search
- \--metaphlan-options
- \--prescreen-threshold
- \--bowtie2-options
- \--nucleotide-identity-threshold
- \--nucleotide-query-coverage-threshold
- \--nucleotide-subject-coverage-threshold"
- \--diamond-options
- \--evalue
- \--translated-identity-threshold
- \--translated-query-coverage-threshold
- \--translated-subject-coverage-threshold
- \--gap-fill
- \--minpath
- \--pathways
- \--xipe
- \--annotation-gene-index
- \--output-format
- \--output-max-decimals
- \--remove-column-description-output
- \--remove-stratified-output

Additional arguments can be specified under the `tool_args` argument.
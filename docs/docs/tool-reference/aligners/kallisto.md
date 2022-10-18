**Kalisto** is a program for quantifying abundances of transcripts from RNA-Seq data. For more information, see the 
tool's [GitHub repo](https://github.com/pachterlab/kallisto). Toolchest only supports running `kallisto quant` with 
pre-built indexes at this time.

# Function Call

```python
tc.kallisto(
  	inputs=[]
  	output_path=None,
  	tool_args="",
  	database_name="kallisto_homo_sapiens",
  	database_version="1",
  	gtf=None, 
  	chromosomes=None,
  	is_async=False,
)
```

## Function Arguments

| Argument           | Use in place of:      | Description                                                                                                                                                                                                              |
| :----------------- | :-------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inputs`           |                       | Path or list of paths to input files for the Kallisto run. The files can be local or remote, see [Using Files](../../getting-started/using-files.md).                                            |
| `output_path`      | output file location  | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be local or remote, see [Using Files](../../getting-started/using-files.md). |
| `tool_args`        | all other arguments   | (optional) Additional arguments to be passed to Kallisto. This should be a string of arguments like the command line.                                                                                                    |
| `database_name`    | `-i`, `--index`       | (optional) Name of database to use for Kallisto alignment. Defaults to `"kallisto_homo_sapiens"`.                                                                                                                        |
| `database_version` | `-i`, `--index`       | (optional) Version of database to use for Kallisto alignment. Defaults to `"1"`.                                                                                                                                         |
| `gtf`              | `-g`, `--gtf`         | (optional) path to a GTF file for transcriptome information (required when using `--genomebam` tool arg). See [the Kallisto manual](http://pachterlab.github.io/kallisto/manual.html) for more info.                     |
| `chromosomes`      | `-c`, `--chromosomes` | (optional) Path to a tab separated file with chromosome names and lengths (recommended when using `--genomebam` tool arg). See [the Kallisto manual](http://pachterlab.github.io/kallisto/manual.html) for more info.    |
| `is_async`         |                       | Whether to run a job asynchronously.  See [Async Runs](../../feature-reference/async-runs.md) for more.                                                                                                                                  |

See the [Databases](#databases) section for more details.

## Notes

### Single-end inputs

Single-end read inputs require `--single`, `--fragment-length` (or `-l`), and `--sd` (or `-s`) to be provided via  `tool_args`. See [the Kallisto manual](http://pachterlab.github.io/kallisto/manual.html) for more info.

# Tool Versions

Toolchest currently supports version **0.48.0** of Kallisto.

# Databases

Toolchest currently supports the following databases for Kallisto:

| `database_name`                     | `database_version` | Description                                                                                                                                                  |
| :---------------------------------- | :----------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `kallisto_homo_sapiens`             | `1`                | Homo sapiens Ensembl v96 index for Kallisto, pulled from <https://github.com/pachterlab/kallisto-transcriptome-indices/releases/tag/ensembl-96>.             |
| `kallisto_caenorhabditis_elegans`   | `1`                | Caenorhabditis elegans Ensembl v96 index for Kallisto, pulled from <https://github.com/pachterlab/kallisto-transcriptome-indices/releases/tag/ensembl-96>.   |
| `kallisto_danio_rerio`              | `1`                | Danio rerio Ensembl v96 index for Kallisto, pulled from <https://github.com/pachterlab/kallisto-transcriptome-indices/releases/tag/ensembl-96>.              |
| `kallisto_drosophila_melanogaster`  | `1`                | Drosophila melanogaster Ensembl v96 index for Kallisto, pulled from <https://github.com/pachterlab/kallisto-transcriptome-indices/releases/tag/ensembl-96>.  |
| `kallisto_gallus_gallus`            | `1`                | Gallus gallus Ensembl v96 index for Kallisto, pulled from <https://github.com/pachterlab/kallisto-transcriptome-indices/releases/tag/ensembl-96>.            |
| `kallisto_mus_musculus`             | `1`                | Mus Musculus Ensembl v96 index for Kallisto, pulled from <https://github.com/pachterlab/kallisto-transcriptome-indices/releases/tag/ensembl-96>.             |
| `kallisto_pan_troglodytes`          | `1`                | Pan Troglodytes Ensembl v96 index for Kallisto, pulled from <https://github.com/pachterlab/kallisto-transcriptome-indices/releases/tag/ensembl-96>.          |
| `kallisto_rattus_norvegicus`        | `1`                | Rattus norvegicus Ensembl v96 index for Kallisto, pulled from <https://github.com/pachterlab/kallisto-transcriptome-indices/releases/tag/ensembl-96>.        |
| `kallisto_saccharomyces_cerevisiae` | `1`                | Saccharomyces cerevisiae Ensembl v96 index for Kallisto, pulled from <https://github.com/pachterlab/kallisto-transcriptome-indices/releases/tag/ensembl-96>. |
| `kallisto_xenopus_tropicalis`       | `1`                | Xenopus tropicalis Ensembl v96 index for Kallisto, pulled from <https://github.com/pachterlab/kallisto-transcriptome-indices/releases/tag/ensembl-96>.       |

# Other modes

Only `quant` mode is supported at this time.
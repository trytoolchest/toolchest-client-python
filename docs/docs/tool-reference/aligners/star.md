**STAR** is an aligner for RNA sequencing. It rapidly aligns RNA-seq reads against a genome index. For more information, see the tool's [GitHub repo and manual](https://github.com/alexdobin/STAR).

Function Call
=============

```python
tc.STAR(
  	read_one,
  	read_two=None,
  	output_path=None,
  	tool_args="",
  	database_name="GRCh38",
  	database_version="1",
  	is_async=False,
)
```

Function Arguments
------------------

See the Notes section below for more details.

| Argument           | Use in place of:      | Description                                                                                                                                                                                                                                      |
| :----------------- | :-------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `read_one`         | `--readFilesIn`       | Paths to single-end read input file, or R1 of paired-end read input files. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                                                  |
| `read_two`         | `--readFilesIn`       | (optional) Path to read 2 of paired-end read input files. This can be a local filepath or an AWS S3 URI.                                                                                                                                         |
| `output_path`      | `--outFileNamePrefix` | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).                       |
| `tool_args`        | all other arguments   | (optional) Additional arguments to be passed to STAR. This should be a string of arguments like the command line. See [Supported Additional Arguments](#supported-additional-arguments) for more details. |
| `database_name`    | `--genomeDir`\*       | (optional) Name of database to use for STAR alignment. Defaults to `"GRCh38"` (human genome).                                                                                                                                                    |
| `database_version` | `--genomeDir`\*       | (optional) Version of database to use for STAR alignment. Defaults to `"1"`.                                                                                                                                                                     |
| `is_async`         |                       | Whether to run a job asynchronously.  See [Async Runs](../../feature-reference/async-runs.md) for more.                                                                                                                                                          |

See the [Databases](#databases) section for more details.

Notes
-----

### Single-end and paired-end inputs

Paired-end read inputs should be specified with both `read_one` and `read_two`.

For single-end read inputs, specify the input as `read_one` argument and omit `read_two`.

Tool Versions
=============

Toolchest currently supports version **2.7.9a** of STAR. Every request to run STAR with Toolchest will default to this version.

Databases
=========

Toolchest currently supports the following databases for STAR:

| `database_name` | `database_version` | Description                                                                                                                    |
| :-------------- | :----------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| `GRCh38`        | `1`                | GRCh38 (human) genome, built from [patch GRCh38.p13](https://www.ncbi.nlm.nih.gov/assembly/GCF_000001405.39) using STAR 2.7.4a |

Supported Additional Arguments
==============================

- `--alignEndsProtrude`
- `--alignEndsType`
- `--alignInsertionFlush`
- `--alignIntronMax`
- `--alignIntronMin`
- `--alignMatesGapMax`
- `--alignSJDBoverhangMin`
- `--alignSJoverhangMin`
- `--alignSJstitchMismatchNmax`
- `--alignSoftClipAtReferenceEnds`
- `--alignSplicedMateMapLmin`
- `--alignSplicedMateMapLminOverLmate`
- `--alignTranscriptsPerReadNmax`
- `--alignTranscriptsPerWindowNmax`
- `--alignWindowsPerReadNmax`
- `--outFilterMatchNmin`
- `--outFilterMismatchNmax`
- `--outFilterMismatchNoverReadLmax`
- `--outFilterMultimapNmax`
- `--outFilterType`
- `--outReadsUnmapped`
- `--outSAMstrandField`
- `--outSAMtype`
- `--quantMode`
- `--quantTranscriptomeBAMcompression`
- `--quantTranscriptomeBan`
- `--readFilesCommand`
- `--readFilesType`
- `--readMapNumber`
- `--readMatesLengthsIn`
- `--readStrand`
- `--runRNGseed`
- `--scoreDelBase`
- `--scoreDelOpen`
- `--scoreGap`
- `--scoreGapATAC`
- `--scoreGapGCAG`
- `--scoreGapNoncan`
- `--scoreGenomicLengthLog2scale`
- `--scoreInsBase`
- `--scoreInsOpen`
- `--scoreStitchSJshift`
- `--seedMultimapNmax`
- `--seedNoneLociPerWindow`
- `--seedPerReadNmax`
- `--seedPerWindowNmax`
- `--seedSearchLmax`
- `--seedSearchStartLmax`
- `--seedSearchStartLmaxOverLread`
- `--seedSplitMin`
- `--sjdbInsertSave`
- `--twopassMode`
- `--winAnchorDistNbins`
- `--winAnchorMultimapNmax`
- `--winBinNbits`
- `--winFlankNbins`
- `--winReadCoverageBasesMin`
- `--winReadCoverageRelativeMin`

Additional arguments can be specified under the `tool_args` argument.
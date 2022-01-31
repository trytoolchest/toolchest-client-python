"""
toolchest_client.tools.tool_args
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This contains lists of custom tool_args that can currently be
processed by Toolchest.

The whitelist is a dict of dicts for each tool, with each tool dict
containing accepted tags as keys and each tag's required number of
following args as the keys' vals.

The blacklist is a list of arguments that we know are not compatible
with Toolchest. A tag that is found in this list will cause the run
to fail.

The dangerlist is a list of arguments that we know will change
the function or structure of the tool. A tag that is found in this
list will cause the run to reduce complexity and validation (e.g.
not parallelization and less validation).

Note: Some tags (e.g., for inputs: "-1", "-2") are filtered out, but
their functionalities are provided via other arguments (e.g.,
user-provided inputs).
"""

VARIABLE_ARGS = "variable"

TOOL_ARG_LISTS = {
    "bowtie2": {
        "whitelist": {
            "-q": 0,
            "--tab5": 0,
            "--tab6": 0,
            "--qseq": 0,
            "-f": 0,
            "-r": 0,
            "-F": 1,
            "-s": 1,
            "-u": 1,
            "-5": 1,
            "-3": 1,
            "--trim-to": 1,
            "--phred33": 0,
            "--phred64": 0,
            "--solexa-quals": 0,
            "--int-quals": 0,
            "--very-fast": 0,
            "--fast": 0,
            "--sensitive": 0,
            "--very-sensitive": 0,
            "--very-fast-local": 0,
            "--fast-local": 0,
            "--sensitive-local": 0,
            "--very-sensitive-local": 0,
            "-N": 1,
            "-L": 1,
            "-i": 1,
            "--n-ceil": 1,
            "--dpad": 1,
            "--gbar": 1,
            "--ignore-quals": 0,
            "--nofw": 0,
            "--norc": 0,
            "--no-1mm-upfront": 0,
            "--end-to-end": 0,
            "--local": 0,
            "--ma": 1,
            "--mp": 1,
            "--np": 1,
            "--rdg": 1,
            "--rfg": 1,
            "--score-min": 1,
            "-k": 1,
            "-a": 0,
            "-D": 1,
            "-R": 1,
            "-I": 1,
            "--minins": 1,
            "-X": 1,
            "--maxins": 1,
            "--fr": 0,
            "--rf": 0,
            "--ff": 0,
            "--no-mixed": 0,
            "--no-discordant": 0,
            "--dovetail": 0,
            "--no-contain": 0,
            "--no-overlap": 0,
            "--align-paired-reads": 0,
            "--preserve-tags": 0,
            "-t": 0,
            "--time": 0,
            "--no-unal": 0,
            "--no-hd": 0,
            "--no-sq": 0,
            "--rg-id": 1,
            "--rg": 1,
            "--omit-sec-seq": 0,
            "--soft-clipped-unmapped-tlen": 0,
            "--sam-no-qname-trunc": 0,
            "--xeq": 0,
            "--sam-append-comment": 0,
            "--qc-filter": 0,
            "--seed": 1,
            "--non-deterministic": 0,
        },
    },
    "cellranger_mkfastq": {
        "whitelist": {
            "--samplesheet": 0,
            # todo: add cellranger mkfastq args
        },
    },
    "kraken2": {
        "whitelist": {
            "--quick": 0,
            "--confidence": 1,
            "--minimum-base-quality": 1,
            "--use-names": 0,
            "--gzip-compressed": 0,
            "--bzip2-compressed": 0,
            "--minimum-hit-groups": 1,
            "--paired": 0,
        },
    },
    "megahit": {
        "blacklist": [
            "--continue",
            "-o",
        ],
        "whitelist": {
            "--min-count": 1,
            "--k-list": 1,
            "--k-min": 1,
            "--k-max": 1,
            "--k-step": 1,
            "--no-mercy": 0,
            "--bubble-level": 1,
            "--merge-level": 1,
            "--prune-level": 1,
            "--prune-depth": 1,
            "--disconnect-ratio": 1,
            "--low-local-ratio": 1,
            "--max-tip-len": 1,
            "--cleaning-rounds": 1,
            "--no-local": 0,
            "--kmin-1pass": 1,
            "--presets": 1,
            "--min-contig-len": 1,
        },
    },
    "shi7": {
        "whitelist": {
            "--debug": 0,
            "--adaptor": VARIABLE_ARGS,
            "-SE": 0,
            "--flash": 1,
            "--trim": 1,
            "-outies": 1,
            "--allow_outies": 1,
            "--convert_fasta": 1,
            "--combine_fasta": 1,
            "-s": 1,
            "-strip_delim": 1,
            "-m": 1,
            "--min_overlap": 1,
            "-M": 1,
            "--max_overlap": 1,
            "-filter_l": 1,
            "--filter_length": 1,
            "-filter_q": 1,
            "--filter_qual": 1,
            "-trim_q": 1,
            "--trim_qual": 1,
            "--drop_r2": 1,
        },
    },
    "STAR": {
        "blacklist": [
            "--runThreadN",
            "--runMode",
            "--outFileNamePrefix",
            "--genomeDir",
            "--sjdbGTFfile",
            "---readFilesIn",
            "--genomeLoad",
        ],
        "dangerlist": [
            "--outReadsUnmapped",
            "--outSAMtype",
            "--readFilesCommand",
            "--sjdbInsertSave",
        ],
        "whitelist": {
            "--alignIntronMin": 1,
            "--alignIntronMax": 1,
            "--alignMatesGapMax": 1,
            "--alignSJoverhangMin": 1,
            "--alignSJstitchMismatchNmax": 1,
            "--alignSJDBoverhangMin": 1,
            "--alignSplicedMateMapLmin": 1,
            "--alignSplicedMateMapLminOverLmate": 1,
            "--alignWindowsPerReadNmax": 1,
            "--alignTranscriptsPerWindowNmax": 1,
            "--alignTranscriptsPerReadNmax": 1,
            "--alignEndsType": 1,
            "--alignEndsProtrude": 1,
            "--alignSoftClipAtReferenceEnds": 1,
            "--alignInsertionFlush": 1,
            "--outFilterType": 1,
            "--outFilterMultimapNmax": 1,
            "--outFilterMismatchNmax": 1,
            "--outFilterMismatchNoverReadLmax": 1,
            "--outFilterMatchNmin": 1,
            "--outReadsUnmapped": 1,  # affects whether we can verify all outputs
            "--outSAMstrandField": 1,
            "--outSAMtype": VARIABLE_ARGS,  # affects whether we can verify all outputs
            "--readFilesCommand": VARIABLE_ARGS,  # affects how we can split input files
            "--runRNGseed": 1,
            "--readFilesType": 1,
            "--readMapNumber": 1,
            "--readMatesLengthsIn": 1,
            "--readStrand": 1,
            "--scoreGap": 1,
            "--scoreGapNoncan": 1,
            "--scoreGapGCAG": 1,
            "--scoreGapATAC": 1,
            "--scoreGenomicLengthLog2scale": 1,
            "--scoreDelOpen": 1,
            "--scoreDelBase": 1,
            "--scoreInsOpen": 1,
            "--scoreInsBase": 1,
            "--scoreStitchSJshift": 1,
            "--seedSearchStartLmax": 1,
            "--seedSearchStartLmaxOverLread": 1,
            "--seedSearchLmax": 1,
            "--seedMultimapNmax": 1,
            "--seedPerReadNmax": 1,
            "--seedPerWindowNmax": 1,
            "--seedNoneLociPerWindow": 1,
            "--seedSplitMin": 1,
            "--sjdbInsertSave": 1,  # affects whether we can verify all outputs
            "--twopassMode": 1,
            "--winAnchorMultimapNmax": 1,
            "--winBinNbits": 1,
            "--winAnchorDistNbins": 1,
            "--winFlankNbins": 1,
            "--winReadCoverageRelativeMin": 1,
            "--winReadCoverageBasesMin": 1,
            "--quantMode": VARIABLE_ARGS,
            "--quantTranscriptomeBAMcompression": 1,
            "--quantTranscriptomeBan": 1,
        },
    },
    "shogun_align": {
        "whitelist": {
            "-a": 1,
            "--aligner": 1,
        },
    },
    "shogun_filter": {
        "whitelist": {
            "-p": 1,
            "--percent-id": 1,
            "-a": 1,
            "--alignment": 1,
        },
    },
    # All user-provided arguments are filtered out for the test pipeline.
    "test": {
        "whitelist": {},
        "blacklist": ["--bad"],
    },
    "unicycler": {
        "whitelist": {
            "--verbosity": 1,
            "--min_fasta_length": 1,
            "--mode": 1,
            "--linear_seqs": 1,
            "--no_correct": 0,
            "--min_kmer_frac": 1,
            "--max_kmer_frac": 1,
            "--kmers": 1,
            "--kmer_count": 1,
            "--depth_filter": 1,
            "--largest_component": 0,
            "--no_miniasm": 0,
            "--no_rotate": 0,
            "--start_gene_id": 1,
            "--start_gene_cov": 1,
            "--no_pilon": 0,
            "--min_polish_size": 1,
            "--min_component_size": 1,
            "--min_dead_end_size": 1,
            "--scores": 1,
            "--low_score": 1,
        },
    },
}

"""
toolchest_client.tools.arg_whitelist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This contains a whitelist for custom tool_args that can currently be
processed by Toolchest.

The whitelist is a dict of dicts for each tool, with each tool dict
containing accepted tags as keys and each tag's required number of
following args as the keys' vals.

Note: Some tags (e.g., for inputs: "-1", "-2") are filtered out, but
their functionalities are provided via other arguments (e.g.,
user-provided inputs).
"""

VARIABLE_ARGS = "variable"

ARGUMENT_WHITELIST = {
    # See http://bowtie-bio.sourceforge.net/bowtie2/manual.shtml for details.
    "bowtie2": {
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
    # Docs at https://cutadapt.readthedocs.io/en/stable/guide.html
    # Paired read inputs are currently unsupported.
    "cutadapt": {
        "-a": 1,
        "--adapter": 1,
        "-g": 1,
        "--front": 1,
        "-b": 1,
        "--anywhere": 1,
        "-e": 1,
        "--error-rate": 1,
        "--errors": 1,
        "--no-indels": 1,
        "-n": 1,
        "--times": 1,
        "-O": 1,
        "--overlap": 1,
        "--match-read-wildcards": 0,
        "-N": 0,
        "--no-match-read-wildcards": 0,
        "--action": 1,
        "--rc": 0,
        "--revcomp": 0,
        "-u": 1,
        "--cut": 1,
        "--nextseq-trim": 1,
        "-q": 1,
        "--quality-cutoff": 1,
        "--quality-base": 1,
        "-l": 1,
        "--length": 1,
        "--trim-n": 0,
        "--length-tag": 1,
        "--strip-suffix": 1,
        "-x": 1,
        "--prefix": 1,
        "-y": 1,
        "--suffix": 1,
        "--rename": 1,
        "--zero-cap": 0,
        "-z": 0,
        "-m": 1,
        "--minimum-length": 1,
        "-M": 1,
        "--maximum-length": 1,
        "--max-n": 1,
        "--max-expected-errors": 1,
        "--max-ee": 1,
        "--discard-trimmed": 0,
        "--discard": 0,
        "--discard-untrimmed": 0,
        "--trimmed-only": 0,
        "--discard-casava": 0,
    },
    # Docs at https://github.com/DerrickWood/kraken2/wiki/Manual
    "kraken2": {
        "--quick": 0,
        "--confidence": 1,
        "--minimum-base-quality": 1,
        "--use-names": 0,
        "--gzip-compressed": 0,
        "--bzip2-compressed": 0,
        "--minimum-hit-groups": 1,
        "--paired": 0,
    },
    # TODO: add STAR arguments to whitelist
    "STAR": {
        "--outFilterType": 1,
        "--outFilterMultimapNmax": 1,
        "--outFilterMismatchNmax": 1,
        "--outFilterMismatchNoverReadLmax": 1,
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
    # All user-provided arguments are filtered out for the test pipeline.
    "test": {},
    # See https://github.com/rrwick/Unicycler#options-and-usage for details.
    "unicycler": {
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
}

"""
toolchest_client.arg_whitelist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This contains a whitelist for custom tool_args that can currently be
processed by Toolchest.

The whitelist is a dict of dicts for each tool, with each tool dict
containing accepted tags as keys and each tag's required number of
following args as the keys' vals.

Note: Some tags (e.g., for inputs: "-1", "-2") are filtered out, but
their functionalities are provided via other arguments (e.g.,
user-provided inputs).
"""

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
    "cutadapt": {
        "-a": 1,
    },
    "kraken2": {

    },
    "test": {},
    "unicycler": {

    },
}
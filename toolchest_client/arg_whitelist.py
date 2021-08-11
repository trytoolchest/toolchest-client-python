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

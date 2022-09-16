import re


def filter_sam(unfiltered_path, filtered_path):
    """
    Filters out non-deterministic metadata lines from a SAM output file.
    """
    with open(filtered_path, "w") as outfile:
        with open(unfiltered_path, "r") as infile:
            outfile.writelines([line for line in infile if not line.startswith("@PG") and not line.startswith("@CO")])


def filter_regex(unfiltered_path, filtered_path, search_regex, replacement_str):
    """
    Filters out non-deterministic metadata lines from a SAM output file.
    """
    with open(filtered_path, "w") as outfile:
        with open(unfiltered_path, "r") as infile:
            for line in infile:
                outfile.write(re.sub(search_regex, replacement_str, line))

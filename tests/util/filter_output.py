def filter_sam(unfiltered_path, filtered_path):
    """
    Filters out non-deterministic metadata lines from a SAM output file.
    """
    with open(filtered_path, "w") as outfile:
        with open(unfiltered_path, "r") as infile:
            outfile.writelines([line for line in infile if not line.startswith("@PG") and not line.startswith("@CO")])

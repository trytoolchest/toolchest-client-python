Taxonomic classifiers perform a fuzzy search between input sequences and reference databases. A classic use-case is 
determining the relative abundance of a microbiome sample.

If you only need relative abundance, you can use a taxonomic profiler that simply returns relative abundance. For a 
more detailed view, you can use a classifier like [Kraken 2](taxonomic-classifiers/kraken-2.md).

Toolchest hosts both the taxonomic classifier and the corresponding reference databases, and you can also 
[use your own custom database](../feature-reference/adding-and-updating-custom-databases.md).

Typically, taxonomic classifiers are more efficient than aligners for taxonomic classification, but most are based on 
heuristic methods rather than optimal alignment scores. If you're looking for something more analogous to BLAST, check 
out [aligners](aligners.md).

If you want to use a taxonomic classifier that's not listed here, let us know! It might even be already available on 
our infrastructure but not listed.
# Aligners

Aligners find the similarity between two or more sequences. Sometimes, query sequences are compared against a reference 
database in a sort of fuzzy search (e.g. [Bowtie 2](aligners/bowtie-2.md)). In other contexts, several query sequences
are compared against one another (e.g. [Clustal Omega](aligners/clustal-omega.md)).

Most aligners are tailored for specific types of data: [STAR](aligners/star.md) for single-cell RNA-Seq, 
[DIAMOND BLASTP](aligners/diamond/diamond-blastp.md) for protein sequences against a protein database, and 
[DIAMOND BLASTX](aligners/diamond/diamond-blastx.md) for translated nucleotide sequences against a protein database.

Toolchest hosts both the aligner and the reference databases, and you can also 
[use your own custom database](../feature-reference/adding-and-updating-custom-databases.md).

If you don't need the extra information that aligners return – e.g. for some microbiome taxonomic classification – 
you can also use a more efficient [classifier](taxonomic-classifiers.md).

If you want to use an aligner that's not listed here, [let us know](https://airtable.com/shrNBkD0bG2wB15jQ)! It might 
already be available on our infrastructure but not documented.
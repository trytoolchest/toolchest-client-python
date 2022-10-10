Workflow tools – or meta-tools – wrap several tools to form a unified pipeline. These workflow tools are usually 
focused specific area like microbiome or single-cell analysis, but they wrap more generic tools under the hood. 

They're popular, because they're easy to use; there's no need to make your own choices on aligners, assemblers, or 
classifiers, and the tools the workflow creator chooses are often pre-tuned for one specific use-case.

[HUMAnN](workflows-meta-tools/humann3.md) is a perfect example of these types of meta-tools. Under the hood, it uses:

- [Bowtie 2](aligners/bowtie-2.md)
- [Diamond](aligners/diamond.md)
- [Python 3](python3.md)
- [RAPSearch2](aligners/rapsearch2.md)
- [MetaPhlAn 3](taxonomic-classifiers/metaphlan.md)

and several other tools, all wrapped under the `humann` command.

When using workflow tools via Toolchest, you'll notice a new argument: `mode`. This lets you run sub-tools directly.
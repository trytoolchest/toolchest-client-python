.. Python Client for Toolchest documentation master file, created by
   sphinx-quickstart on Wed May 26 18:41:37 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Toolchest Client Documentation
=======================================================

**Toolchest** is an API for bioinformatic data analysis.
It allows you to abstract away the costliness of running tools on your
own resources by running the same jobs on secure, powerful remote
servers.

Using a tool in Toolchest is as simple as:

    >>> import toolchest_client as toolchest
    >>> toolchest.set_key("YOUR_TOOLCHEST_KEY")
    >>> toolchest.your_tool_name(
    ...     tool_args="YOUR_CUSTOM_TOOL_ARGS",
    ...     inputs="path/to/input",
    ...     output_path="path/to/output",
    ... )

.. _tools:

Tools
-----

Toolchest currently supports the following tools:

* Bowtie2 (`bowtie2`)
* Cutadapt (`cutadapt`)
* Kraken2 (`kraken2`)
* STAR (`STAR`)
* Unicycler (`unicycler`)


User Guide
----------

Info on installing and getting started can be found here.

.. toctree::
    :maxdepth: 2

    user/install
    user/quickstart

API Documentation
-----------------

For specific function-related info and documentation, see here.

.. toctree::
    :maxdepth: 2

    api

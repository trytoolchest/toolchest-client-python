.. _quickstart:

Quickstart
==========

This page gives an intro on how to get started with the Toolchest client.

First, make sure that:

* The Toolchest client is :ref:`installed <install>`, which you can do via::

    $ pip install toolchest-client

* The Toolchest client is up-to-date (be sure to use the latest version,
  currently |version|)
* You have an :ref:`authentication key <config>`

..
  TODO: figure out how to bold the version number

.. _config:

Configuring Your Client
-----------------------

Toolchest requires an authentication key in order to process queries.

You can obtain a key by `signing up for a trial of Toolchest
<https://airtable.com/shrKzQNuDHrGkEAI2>`_.

`Contact Toolchest <founders@trytoolchest.com>`_ if:

* you've forgotten your key
* the key is producing authentication errors.

Once you have an authentication key, configure your client as follows:

    >>> import toolchest_client as toolchest
    >>> toolchest.set_key(YOUR_TOOLCHEST_KEY)

The variable `YOUR_TOOLCHEST_KEY` can be either a string containing your
key or a path to a file containing the key (and nothing else).

Sample Data
-----------

To use Toolchest tools, you will need input files.

A sample FASTQ input file (~50MB) can be downloaded
`via this link <https://toolchest-demo-data.s3.amazonaws.com/example.fastq>`_.

Using Tools
-----------

To use a data analysis tool, you would probably run a command like this on the
command line::

    $ your_tool YOUR_CUSTOM_TOOL_ARGS

Once Toolchest is configured, you can do the same with the corresponding
Toolchest function:

>>> import toolchest_client as toolchest
>>> toolchest.your_tool(
...     tool_args="YOUR_CUSTOM_TOOL_ARGS",
...     inputs="path/to/input",
...     output_path="path/to/output",
... )

Here, `your_tool` is the name of the command that you would use, and
`YOUR_CUSTOM_TOOL_ARGS` is a string containing all the arguments that you would
normally pass to the tool, outside of input and output filepath arguments.

Note that `YOUR_CUSTOM_TOOL_ARGS` should **not** include any arguments related
to the input and output file paths; these will be automatically handled by the
Toolchest backend, and including these arguments will lead to undesired output.

For a full list of available tools, see :ref:`this list <tools>`.

Not all functionalities of available tools can be used. See the
relevant :ref:`in-depth tool documentation <api>` or contact Toolchest
for details.

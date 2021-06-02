.. _quickstart:

Quickstart
==========

This page gives an intro on how to get started with the Toolchest client.

First, make sure that:

* The Toolchest client is :ref:`installed <install>`
* The Toolchest client is up-to-date
* You have an :ref:`authentication key <Configuring Your Client>`

Configuring Your Client
-----------------------

Toolchest requires an authentication key in order to process queries.

Contact Toolchest if:

* you need a key
* you've forgotten your key
* the key is producing authentication errors.

Once you have an authentication key, configure your client as follows:

``` python
import toolchest_client as tc
tc.set_key(YOUR_TOOLCHEST_KEY)
```

The variable `YOUR_TOOLCHEST_KEY` can be either a string containing your
key or a path to a file containing the key (and nothing else).

Using Tools
-----------

To use a data analysis tool, you would probably run a command like this on the
command line:

    $ your_tool YOUR_CUSTOM_TOOL_ARGS

Once Toolchest is configured, you can do the same with the corresponding
Toolchest function:

``` python
import toolchest_client as tc
tc.your_tool(
    YOUR_CUSTOM_TOOL_ARGS,
    input_path="path/to/your/input",
    output_path="path/to/your/output",
)
```

Here, `your_tool` is the name of the command that you would use, and
`YOUR_CUSTOM_TOOL_ARGS` is a string containing all the arguments that you would
normally pass to the tool.

Note that `YOUR_CUSTOM_TOOL_ARGS` should **not** include any arguments related
to the input and output file paths; these will be automatically handled by the
Toolchest backend, and including these arguments will lead to undesired output.

For a full list of available tools, see :ref:`this list <tools>`.

Not all functionalities of available tools can be used. See the
relevant `in-depth tool documentation <api>` for details.

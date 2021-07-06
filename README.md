# Toolchest Python Client

**Toolchest** provides APIs for scientific and bioinformatic data analysis.
It allows you to abstract away the costliness of running tools on your
own resources by running the same jobs on secure, powerful remote
servers.

This package contains the **Python** client for using Toolchest.
For the **R** client, [see here](https://github.com/trytoolchest/toolchest-client-r).

## Installation

The Toolchest client is available [on PyPI](https://pypi.org/project/toolchest-client):
``` shell
pip install toolchest-client
```

## Usage

Using a tool in Toolchest is as simple as:

``` python
import toolchest_client as toolchest
toolchest.set_key("YOUR_TOOLCHEST_KEY")
toolchest.kraken2(
  tool_args="",
  inputs="path/to/input.fastq",
  output_path="path/to/output.fastq",
)
```

For a list of available tools, see the [documentation](https://toolchest-python-client.readthedocs.io/en/latest/).

## Configuration

To use Toolchest, you must have an authentication key stored
in the `TOOLCHEST_KEY` environment variable.

``` python
import toolchest_client as toolchest
toolchest.set_key("YOUR_TOOLCHEST_KEY") # or a file path containing the key
```

Contact Toolchest if:

-   you need a key
-   you’ve forgotten your key
-   the key is producing authentication errors.

## Documentation & User Guide available at [Read the Docs](https://toolchest-python-client.readthedocs.io/en/latest/)

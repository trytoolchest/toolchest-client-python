!!! warning "This probably isn't the page you're looking for"
    To run Python functions and Docker images with Toolchest, check out [Lug](https://lug.dev), an open-source 
    project that builds on Toolchest.


Python is the favorite language of many computational biologists. Unfortunately, running Python on your computer reaches its limits quickly while analyzing biological data. The way most researchers get more power is by starting a cloud instance, SSHing in, and running their Python script in the cloud.

Companies like Stripe have [internal tooling](https://stripe.com/blog/railyard-training-models) for their engineers to train machine learning models in the cloud. It replaces the process of starting a cloud instance, SSHing in, starting the script, and then copying the results.

You get the same tooling with Toolchest: in the background, Toolchest starts a cloud instance, runs your script on the instance, and copies the input and output files. You only get charged when your script is running on the instance, which means you don't have to pay for idling cloud instances – or pay thousands of dollars after forgetting to terminate instances.

Example usage
=============

Let's say we want to:

1. Calculate the length of `input.txt` with a Python script called `calculate_length.py`
2. Return the length of a file at `./my_output/length.txt`

The Toolchest call is:

```python
file_to_count = "input.txt"
length_file = "length.txt"

tc.python3(
    script="calculate_length.py",
    inputs=[file_to_count],
    output_path="./my_output/",
    tool_args=f"--input-file {file_to_count} --length-file {length_file}",
)
```

In the Python script, inputs are read from `./input/`, and output is written to `./output/`. That's because Toolchest places input files at `./input/`, and it only captures output files written to `./output/`.

The script, `calculate_length.py`, contains:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input-file', metavar='input', help="Input file")
parser.add_argument('--length-file', metavar='length', help="Output file")
args = parser.parse_args()

with open(f"./input/{args.input}", "r") as input_file:
    input_file_contents = input_file.read()

with open(f"./output/{args.length}", "w") as output_file:
    output_file.write(f"{len(input_file_contents)}")
```

The Toolchest call
==================

```python
tc.python3(
  	script,
  	inputs,
  	output_path=None,
  	tool_args="",
  	is_async=False,
  	streaming_enabled=True,
)
```
```r
toolchest$python3(
    script,
  	inputs,
  	output_path = NULL,
  	tool_args = "",
  	is_async = FALSE
)
```

Custom environments
-------------------

By passing a Docker image to Toolchest using `custom_docker_image_id`, you can run Python in any environment you'd like via Toolchest.

Make sure that the Docker image you use:

- Has `python3` (i.e. `docker run {image} python3` works)
- Supports the `linux/amd64` platform
- Exists on the machine where you're running Toolchest, and that the Docker engine is running

If you're building the image on an M1 Mac or Windows machine, make sure you build your Docker image with platform set to `linux/amd64`.

### Building and using a custom environment

In this guide, we'll build and run a custom Docker image that supports numpy via Toolchest.

Before starting, make sure that [Docker engine is installed](https://docs.docker.com/engine/install/) and running.

Start by creating a file named `Dockerfile` that contains Python 3.9 and numpy:

```dockerfile Dockerfile
FROM python:3.9
RUN pip install numpy
```

Next, build a Docker image from that Dockerfile.

```shell
docker build . -t python3-numpy:3.9 --platform linux/amd64
```
```python
# Make sure the Docker Python library is installed (e.g. pip install docker)
import docker 

client = docker.from_env()
client.images.build(
  path=f"./", # This is a path to the location of the Dockerfile
  dockerfile="Dockerfile",
  tag="python3-numpy:3.9",
  platform="linux/amd64"
) 
```

Now let's make a Python script ("numpy_example.py") that uses numpy:

```python
import numpy as np

a = np.array([(1, 2, 3), (4, 5, 6)])
b = np.array([(7, 8), (9, 10), (11, 12)])
output_string = np.array_str(np.matmul(a, b))

f = open("./output/output.txt", "w")
f.write()
f.close()
```

And finally, the last step: you can run the Python script in the custom Docker image using Toolchest:

```python
import toolchest_client as tc

tc.python3(
    script="numpy_example.py",
    output_path=f"./local_output/",
    custom_docker_image_id="python3-numpy:3.9"
)
```

 That's it!

Python versions
---------------

Toolchest currently runs version **3.9.1** of Python. You can use other versions of Python by using a custom environment.

Passing arguments to your Python 3 script
-----------------------------------------

Any arguments passed to `tool_args` are passed to your Python script, as if it were executing on the command line. For example:

```python
tc.python3(
    script="my_script.py",
    tool_args="--my-arg 1234",
    ...
)
```

Is processed as if the script were run on the command line like:

```shell
python3 my_script.py --my-arg 1234
```

Some argument names are not allowed due to conflicts with Python itself, including:

- `-c`
- `-i`
- `-m`

Return value
------------

This function call returns a Toolchest output object, which contains the run ID and locations of downloaded output files. See [Output Objects](../feature-reference/output-objects.md).

Async runs
----------

Set the `is_async` parameter to `True` if you would like to run a Python 3 job asynchronously. See [Async Runs](../feature-reference/async-runs.md).
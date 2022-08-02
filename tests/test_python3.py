import os

import docker
import pytest

import toolchest_client as toolchest

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)


@pytest.mark.integration
def test_python3():
    """
    Tests python3 tool's inputs, output, and tool_arg
    """

    test_dir = "./temp_test_python3"
    os.makedirs(f"{test_dir}", exist_ok=True)
    toolchest.python3(
        tool_args="./input/example.fastq",
        script="s3://toolchest-integration-tests/write_test.py",
        inputs="s3://toolchest-integration-tests/example.fastq",
        output_path=f"{test_dir}/",
    )

    output_file = open(f"{test_dir}/output.txt", "r")
    assert output_file.readline() == "Success"
    output_file.close()


def test_python3_with_docker():
    """
    Tests adding dependencies to python3 via a custom docker image

    Specifically tests matrix multiplication via numpy
    """
    client = docker.from_env()
    client.images.build(
        path="./util/numpy_test.Dockerfile",
        dockerfile="numpy_test.Dockerfile",
        tag="python3-numpy:3.9",
        platform="linux/amd64"
    )

    test_dir = "./temp_test_python3"
    os.makedirs(f"{test_dir}", exist_ok=True)
    toolchest.python3(
        script="s3://toolchest-integration-tests/numpy_test.py",
        output_path=f"{test_dir}/",
        custom_docker_image_id="python3-numpy:3.9"
    )

    output_file = open(f"{test_dir}/output.txt", "r")
    assert output_file.readline() == "[[ 58  64]\n"
    assert output_file.readline() == " [139 154]]"
    output_file.close()

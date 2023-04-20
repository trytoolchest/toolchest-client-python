import io
import os
import pathlib
import sys

import docker
import pytest

import toolchest_client as toolchest
from toolchest_client.api.instance_type import InstanceType

toolchest_api_key = os.environ.get("TOOLCHEST_API_KEY")
if toolchest_api_key:
    toolchest.set_key(toolchest_api_key)

THIS_FILE_PATH = pathlib.Path(__file__).parent.resolve()


@pytest.mark.integration
def test_python3():
    """
    Tests python3 tool's inputs, output, and tool_arg

    NOTE: streaming is disabled for this test
    """

    test_dir = "./temp_test_python3"
    os.makedirs(f"{test_dir}", exist_ok=True)
    toolchest.python3(
        tool_args="./input/example.fastq",
        script="s3://toolchest-integration-tests/write_test.py",
        inputs="s3://toolchest-integration-tests/example.fastq",
        output_path=f"{test_dir}/",
        instance_type=InstanceType.COMPUTE_2,
        streaming_enabled=False,
    )

    output_file = open(f"{test_dir}/output.txt", "r")
    assert output_file.readline() == "Success"
    output_file.close()


@pytest.mark.integration
def test_python3_with_docker():
    """
    Tests adding dependencies to python3 via a custom docker image

    Specifically tests matrix multiplication via numpy
    """
    client = docker.from_env()
    client.images.build(
        path=f"{THIS_FILE_PATH}/util/",
        dockerfile="numpy_test.Dockerfile",
        tag="python3-numpy:3.9",
        platform="linux/amd64"
    )

    test_dir = "./temp_test_python3/with_docker"
    os.makedirs(f"{test_dir}", exist_ok=True)
    toolchest.python3(
        script="s3://toolchest-integration-tests/numpy_test.py",
        output_path=f"{test_dir}/",
        custom_docker_image_id="python3-numpy:3.9",
        instance_type="compute-2",
    )

    output_file = open(f"{test_dir}/output.txt", "r")
    assert output_file.readline() == "[[ 58  64]\n"
    assert output_file.readline() == " [139 154]]"
    output_file.close()


@pytest.mark.integration
def test_python3_with_public_docker():
    """
    Tests using a public docker image with the write test script
    """

    test_dir = "./temp_test_python3/with_public_docker"
    os.makedirs(f"{test_dir}", exist_ok=True)
    toolchest.python3(
        script="s3://toolchest-integration-tests/write_path.py",
        output_path=f"{test_dir}/",
        custom_docker_image_id="python:alpine3.16",
    )

    output_file = open(f"{test_dir}/output.txt", "r")
    assert output_file.readline() == "['/data/home/ec2-user/persist/input', '/usr/local/lib/python311.zip', " \
                                     "'/usr/local/lib/python3.11', '/usr/local/lib/python3.11/lib-dynload', " \
                                     "'/usr/local/lib/python3.11/site-packages']"
    output_file.close()


@pytest.mark.integration
def test_python3_streaming():
    """
    Tests python3 with output streaming enabled
    """
    test_dir = "./temp_test_python3_streaming"
    os.makedirs(f"{test_dir}", exist_ok=True)
    test_script_path = "tests/util/streaming_script.py"

    # Run with captured stdout
    captured_stdout = io.StringIO()
    sys.stdout = captured_stdout
    toolchest.python3(
        script=test_script_path,
        output_path=f"{test_dir}/",
        instance_type=InstanceType.COMPUTE_2,
        streaming_enabled=True,
    )
    # Reset stdout capture
    sys.stdout = sys.__stdout__

    # Verify toolchest.python3() output files
    with open(f"{test_dir}/output.txt", "r") as output_file:
        assert output_file.readline() == "Success"

    # Check printed stdout
    stdout_lines = captured_stdout.getvalue().splitlines()
    stream_start = stdout_lines.index("==> Begin streamed lines <==")
    stream_end = stdout_lines.index("==> End streamed lines <==")
    streamed_lines = stdout_lines[stream_start:stream_end + 1]
    assert streamed_lines == ["==> Begin streamed lines <==", "0", "1", "2", "3", "4", "==> End streamed lines <=="]

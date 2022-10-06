import os
import pathlib

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
    """

    test_dir = "./temp_test_python3"
    os.makedirs(f"{test_dir}", exist_ok=True)
    toolchest.python3(
        tool_args="./input/example.fastq",
        script="s3://toolchest-integration-tests/write_test.py",
        inputs="s3://toolchest-integration-tests/example.fastq",
        output_path=f"{test_dir}/",
        instance_type=InstanceType.COMPUTE_2,
        streaming_enabled=False,  # TODO: confirm that this works w/ streaming and remove
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
        streaming_enabled=False,  # TODO: confirm that this works w/ streaming and remove
    )

    output_file = open(f"{test_dir}/output.txt", "r")
    assert output_file.readline() == "[[ 58  64]\n"
    assert output_file.readline() == " [139 154]]"
    output_file.close()


@pytest.mark.integration
def test_python3_streaming():
    test_dir = "./temp_test_python3_streaming"
    os.makedirs(f"{test_dir}", exist_ok=True)
    test_script_path = f"{test_dir}/test_script.py"

    with open(test_script_path, "w") as test_script_file:
        script = """
import datetime
import time
print("attempting to print timestamps every second")
for _ in range(5):
    message = datetime.datetime.utcnow().isoformat() + "Z"
    print(message)
    time.sleep(1)
with open("./output/output.txt", "w") as f:
    f.write("Success")
            """
        test_script_file.write(script)

    toolchest.python3(
        script=test_script_path,
        output_path=f"{test_dir}/",
        instance_type=InstanceType.COMPUTE_2,
        streaming_enabled=True,
    )

    # test -- commented out for now
    # output_file = open(f"{test_dir}/output.txt", "r")
    # assert output_file.readline() == "Success"
    # output_file.close()

    # TODO: add asserts on streamed output

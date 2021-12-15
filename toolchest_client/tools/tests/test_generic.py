import os
import pytest

from ..test import Test

THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def test_unknown_arg_handling():
    tool_args = f"--unknown arg"
    test_instance = Test(
        tool_args=tool_args,
        inputs=f"{THIS_DIRECTORY}/test_generic.py",
        output_path="./output.tar.gz",
        output_name='output',
    )

    with pytest.raises(ValueError):
        test_instance._validate_args()


def test_blacklisted_arg_handling():
    tool_args = f"--bad arg"
    test_instance = Test(
        tool_args=tool_args,
        inputs=f"{THIS_DIRECTORY}/test_generic.py",
        output_path="./output.tar.gz",
        output_name='output',
    )

    with pytest.raises(ValueError):
        test_instance._validate_args()

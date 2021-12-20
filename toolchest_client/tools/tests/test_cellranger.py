import os

from ..cellranger import CellRangerMkfastq

THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def test_cellranger_equal_sign_tool_arg_parsing():
    tool_args = f"--samplesheet=test.sample!sheet.name.csv"
    cellranger_mkfastq_instance = CellRangerMkfastq(
        tool_args=tool_args,
        inputs=f"{THIS_DIRECTORY}/test_cellranger.py",
        output_path="./output.tar.gz",
        output_name='output',
    )
    cellranger_mkfastq_instance._validate_args()

    assert cellranger_mkfastq_instance.tool_args == tool_args

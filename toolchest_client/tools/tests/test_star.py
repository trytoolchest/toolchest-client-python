import os

from ..star import STARInstance

THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def test_star_variable_arg_parsing_single():
    star_instance = STARInstance(
        tool_args="--quantMode GeneCounts --scoreGap 1",
        output_name='Aligned.out.sam',
        input_prefix_mapping={
            "r1_path": None,
            "r2_path": None,
        },
        inputs=f"{THIS_DIRECTORY}/test_star.py",
        output_path="./",
        database_name="test",
        database_version="0.1.0",
        parallelize=False,
    )
    star_instance._validate_args()

    assert star_instance.tool_args == "--quantMode GeneCounts --scoreGap 1"


def test_star_variable_arg_parsing_multiple():
    star_instance = STARInstance(
        tool_args="--quantMode TranscriptomeSAM GeneCounts --scoreGap 1",
        output_name='Aligned.out.sam',
        input_prefix_mapping={
            "r1_path": None,
            "r2_path": None,
        },
        inputs=f"{THIS_DIRECTORY}/test_star.py",
        output_path="./",
        database_name="test",
        database_version="0.1.0",
        parallelize=False,
    )
    star_instance._validate_args()

    assert star_instance.tool_args == "--quantMode TranscriptomeSAM GeneCounts --scoreGap 1"

from .. import convert_input_params_to_prefix_mapping


def test_generate_prefix_mapping():
    tag_to_param_map = {
        "-1": ["example1_R1.fastq", "example2_R1.fastq"],
        "-2": ["example1_R2.fastq", "example2_R1.fastq"],
        "-U": ["example1_U.fastq", "example2_U.fastq"],
    }
    prefix_mapping = convert_input_params_to_prefix_mapping(tag_to_param_map)
    assert prefix_mapping == {
        "example1_R1.fastq": {
            "prefix": "-1",
            "order": 0,
        },
        "example1_R2.fastq": {
            "prefix": "-2",
            "order": 0,
        },
        "example1_U.fastq": {
            "prefix": "-U",
            "order": 0,
        },
        "example2_R1.fastq": {
            "prefix": "-1",
            "order": 1,
        },
        "example2_R2.fastq": {
            "prefix": "-2",
            "order": 1,
        },
        "example2_U.fastq": {
            "prefix": "-U",
            "order": 1,
        },
    }

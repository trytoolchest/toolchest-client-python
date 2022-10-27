"""
toolchest_client.files.input_util
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Utilities for handling input files/paths.
"""


# TODO: add unit test
def convert_input_params_to_prefix_mapping(tag_to_param_map):
    """
    Parses input parameters in a Toolchest call into:
    - a list of all input paths (for uploading)
    - a mapping of inputs to their respective prefixes

    Example input params map:
    {
        "-1": [example_R1.fastq],
        "-2": [example_R2.fastq],
        "-U": [example_U.fastq],
    }

    Example output list:
    [example_R1.fastq, example_R2.fastq, example_U.fastq]

    Example output prefix mapping:
    {
        "example_R1.fastq": {
            "prefix": "-1",
            "order": 0,
        },
        "example_R2.fastq": {
            "prefix": "-2",
            "order": 0,
        },
        "example_U.fastq": {
            "prefix": "-U",
            "order": 0,
        },
    }
    """
    input_list = []  # list of all inputs
    input_prefix_mapping = {}  # map of each input to its respective tag
    for tag, param in tag_to_param_map.items():
        if isinstance(param, list):
            for index, input_file in enumerate(param):
                input_list.append(input_file)
                input_prefix_mapping[input_file] = {
                    "prefix": tag,
                    "order": index,
                }
        elif isinstance(param, str):
            input_list.append(param)
            input_prefix_mapping[param] = {
                "prefix": tag,
                "order": 0,
            }
    return input_list, input_prefix_mapping



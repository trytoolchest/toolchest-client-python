import os

from ..kraken2 import Kraken2

THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def test_kraken2_preflight():
    output_path = f"{THIS_DIRECTORY}/output"
    kraken_instance = Kraken2(
        tool_args="",
        output_name='output.tar.gz',
        inputs=f"{THIS_DIRECTORY}/test_kraken2.py",
        output_path=output_path,
        database_name="standard",
        database_version=1,
    )
    kraken_instance._preflight()

    assert os.path.isdir(output_path)
    os.rmdir(output_path)

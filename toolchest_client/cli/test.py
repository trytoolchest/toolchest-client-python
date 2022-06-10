from typing import List

import typer

from toolchest_client.tools import Test

app = typer.Typer()


@app.command()
def test(
    inputs: List[str],
    output_path: str = typer.Option(None, help='Sets the directory where the success file will be downloaded'),
    is_async: bool = typer.Option(False, '--is_async', help='Executes the Toolchest job as an async job')
):
    """
    Confirms that you are able to run toolchest
    """
    test_instance = Test(
        tool_args='',
        output_name='output.tar.gz',
        inputs=inputs,
        output_path=output_path,
        is_async=is_async,
    )
    test_instance.run()


if __name__ == "__main__":
    app()

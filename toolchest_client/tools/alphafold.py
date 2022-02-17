"""
toolchest_client.tools.AlphaFold
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the AlphaFold implementation of the Tool class.
"""
from toolchest_client.files import OutputType
from datetime import date
from . import Tool


class AlphaFold(Tool):
    """
    The AlphaFold implementation of the Tool class.
    """
    def __init__(self, inputs, output_path, model_preset=None, max_template_date=None, use_reduced_dbs=False,
                 is_prokaryote_list=None, **kwargs):
        tool_args = (
            (f"--model_preset={model_preset} " if model_preset is not None else "") +
            (f"--max_template_date={max_template_date} " if max_template_date is not None
             else f"--max_template_date={date.today().strftime('%Y-%m-%d')} ")  # +
            # (f"--is_prokaryote_list={is_prokaryote_list.join(',')} " if is_prokaryote_list is not None else "") +
            # ("--db_preset=reduced_dbs " if use_reduced_dbs else "")
        )
        super().__init__(
            tool_name="alphafold",
            tool_version="2.1.2",
            tool_args=tool_args,
            output_name='output.tar.gz',
            inputs=inputs,
            min_inputs=1,
            max_inputs=1,  # May need to be increased in future
            database_name="alphafold_standard",
            database_version="2.1.2",
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            output_path=output_path,
            output_is_directory=True,
            **kwargs,
        )

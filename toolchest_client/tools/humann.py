"""
toolchest_client.tools.humann
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the HUMAnN implementation of the Tool class.
"""
from enum import Enum

from toolchest_client.files import OutputType

from . import Tool


class HUMAnN3(Tool):
    """
    The HUMAnN implementation of the Tool class.
    """
    def __init__(self, tool_args, inputs, output_primary_name, input_prefix_mapping, output_path, **kwargs):
        super().__init__(
            tool_name="humann3",
            tool_version="3.1.1",  # todo: allow version to be set by the user
            database_name="humann3_protein_uniref90_diamond",
            database_version="1",
            tool_args=tool_args,
            output_path=output_path,
            output_primary_name=output_primary_name,
            inputs=inputs,
            input_prefix_mapping=input_prefix_mapping,
            parallel_enabled=False,
            output_type=OutputType.GZ_TAR,
            **kwargs,
        )


class HUMAnN3Mode(Enum):
    HUMANN = ("humann", False)
    HUMANN_BARPLOT = ("humann_barplot", True)
    HUMANN_GENE_FAMILIES_GENUS_LEVEL = ("humann_genefamilies_genus_level", True)
    HUMANN_JOIN_TABLES = ("humann_join_tables", True)
    HUMANN_REDUCE_TABLE = ("humann_reduce_table", True)
    HUMANN_REGROUP_TABLE = ("humann_regroup_table", True)
    HUMANN_RENORM_TABLE = ("humann_renorm_table", True)
    HUMANN_SPLIT_STRATIFIED_TABLE = ("humann_split_stratified_table", False)
    HUMANN_UNPACK_PATHWAYS = ("humann_unpack_pathways", True)

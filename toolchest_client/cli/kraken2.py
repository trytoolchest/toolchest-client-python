from toolchest_client.tools import Kraken2
from typing import List
import typer
import os

app = typer.Typer()


def verify_kraken2_db(database_name):
    return 'standard', 1  # Todo: implement with healing


def kraken2(
        inputs: List[str],
        db: str = typer.Option(..., help='The name of the database to use'),
        report: str = typer.Option(None, help='Sets the output directory for the results (any file name is ignored '
                                              'and the containing directory is used instead)'),
        threads: int = typer.Option(None, help='Performance parameters are not user specifiable on Toolchest and will '
                                               'be dropped'),
        quick: bool = typer.Option(False, '--quick', help='Rather than searching all l-mers in a sequence, stop '
                                                          'classification after the first database hit'),
        confidence: float = typer.Option(None, help='Sets the confidence threshold used for labelling'),
        minimum_base_quality: int = typer.Option(None, help='Minimum base quality used in classification (def: 0, '
                                                            'only effective with FASTQ input)'),
        use_names: bool = typer.Option(False, '--use_names', help='Replaces the taxonomy ID column with the '
                                                                  'scientific name and the taxonomy ID in '
                                                                  'parenthesis'),
        gzip_compressed: bool = typer.Option(False, '--gzip_compressed', help='Specifies that the input files are '
                                                                              'gzip compressed'),
        bzip2_compressed: bool = typer.Option(False, '--bzip2_compressed', help='Specifies that the input files are '
                                                                                'bzip2 compressed'),
        minimum_hit_groups: int = typer.Option(None, help='Requires multiple hit groups be found before declaring a '
                                                          'sequence classified'),
        paired: bool = typer.Option(False, '--paired', help='Indicate that the input files provided are paired read '
                                                            'data'),
        is_async: bool = typer.Option(False, '--is_async', help='Executes the Toolchest job as an async job'),
        classified_out: str = typer.Option(None, help='Currently not allowed by Toolchest and will be dropped'),
        unclassified_out: str = typer.Option(None, help='Currently not allowed by Toolchest and will be dropped'),
        report_zero_counts: bool = typer.Option(False, '--report_zero_counts', help='Currently not allowed by '
                                                                                    'Toolchest and will be dropped'),
        use_mpa_style: bool = typer.Option(False, '--use_mpa_style', help='Currently not allowed by Toolchest and '
                                                                          'will be dropped'),
):
    """
    Runs kraken2 via Toolchest
    """
    tool_args = ''
    if quick:
        tool_args += '--quick '
    if confidence is not None:
        tool_args += f'--confidence {confidence} '
    if minimum_base_quality is not None:
        tool_args += f'--minimum-base-quality {minimum_base_quality} '
    if use_names:
        tool_args += '--use-names '
    if gzip_compressed:
        tool_args += '--gzip-compressed '
    if bzip2_compressed:
        tool_args += '--bzip2-compressed '
    if minimum_hit_groups is not None:
        tool_args += f'--minimum-hit-groups {minimum_hit_groups} '
    if paired:
        tool_args += '--paired '
    if classified_out is not None:
        print('Dropping --classified_out as it is not currently allowed by Toolchest')
    if unclassified_out is not None:
        print('Dropping --unclassified_out as it is not currently allowed by Toolchest')
    if use_mpa_style:
        print('Dropping --use_mpa_style as it is not currently allowed by Toolchest')
    if report_zero_counts:
        print('Dropping --report_zero_counts as it is not currently allowed by Toolchest')
    if threads is not None:
        print('Dropping --threads as Toolchest manages performance for you')
    database_name, database_version = verify_kraken2_db(db)
    custom_database_path = db if db.startswith('s3://') else None
    output_path = None if report is None else os.path.abspath(os.path.dirname(report))
    kraken2_instance = Kraken2(
        tool_args=tool_args,
        output_name='output.tar.gz',
        output_path=output_path,
        inputs=inputs,
        database_name=database_name,
        database_version=database_version,
        custom_database_path=custom_database_path,
        is_async=is_async,
    )
    kraken2_instance.run()


if __name__ == "__main__":
    app()

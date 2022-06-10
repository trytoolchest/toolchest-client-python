import os
import sys
from typing import List

import requests
import typer
from requests.exceptions import HTTPError

from toolchest_client import get_api_url, ToolchestJobError
from toolchest_client.api.auth import get_headers
from toolchest_client.tools import Kraken2

app = typer.Typer()


def get_kraken2_version_info(database_name):
    response = requests.get(
        get_api_url() + "/tools/kraken2/version-data",
        headers=get_headers(),
    )
    try:
        response.raise_for_status()
    except HTTPError:
        raise ToolchestJobError("Failed to retrieve tool and database info.")
    version_data = response.json()
    tool_versions = version_data.keys()
    tool_version = list(version_data.keys())[0]
    if len(tool_versions) > 1:
        prompt_p1 = 'Multiple tool versions found:\n\t'
        prompt_p2 = 'Select which version of kraken2 you want to run on'
        ver_str = '\n\t'.join(tool_versions)
        tool_version = typer.prompt(prompt_p1 + ver_str + prompt_p2).strip()
        while tool_version not in tool_versions:
            prompt_p1 = 'Unable to process selected version. Please select a version from the list below:\n\t'
            tool_version = typer.prompt(prompt_p1 + ver_str + prompt_p2).strip()
    database_names_for_version = list(map(lambda e: e['database_name'], version_data[tool_version]))
    selected_db_name = database_name
    if database_name in database_names_for_version:
        dbs_with_name = list(filter(lambda e: e['database_name'] == database_name, version_data[tool_version]))
        if len(dbs_with_name) == 1:
            selected_db_version = dbs_with_name[0]['database_version']
        else:
            db_versions = '\n\t'.join(list(map(lambda e: e['database_version'], dbs_with_name)))
            prompt_p1 = f'Multiple versions of database {database_name} found:\n\t'
            prompt_p2 = 'Please enter the version you wish to use'
            selected_db_version = typer.prompt(prompt_p1 + db_versions + prompt_p2).strip()
            while selected_db_version not in db_versions:
                prompt_p1 = 'Unable to process selected version.\n\t'
                prompt_p2 = '\nPlease select a version from the list above'
                selected_db_version = typer.prompt(prompt_p1 + db_versions + prompt_p2).strip()
    else:
        if len(version_data[tool_version]) == 1:
            selected_db_name = version_data[tool_version][0]['database_name']
            selected_db_version = version_data[tool_version][0]['database_version']
            typer.echo(f'Unable to find database {database_name} for Kraken2 {tool_version}.\n'
                       f'Using {selected_db_name} version {selected_db_version} instead.')
        else:
            database_pairs = list(map(lambda db: db['database_name'] + ", " + db['database_version'],
                                      version_data[tool_version]))
            database_strings = ''
            for i in range(0, len(database_pairs)):
                database_strings += f'\n\t{i + 1}) {database_pairs[i]}'
            prompt_p1 = f'Could not find the database: {database_name}. Available databases (name, version) are:'
            prompt_p2 = '\nPlease select the number of the database, version pair you wish to use'
            chosen_db = typer.prompt(prompt_p1 + database_strings + prompt_p2, type=int) - 1
            while not 0 <= chosen_db < len(database_pairs):
                prompt_p1 = 'Unable to process selected version. '
                prompt_p2 = '\nType the number (1, 2, 3...) of the database you wish to use'
                chosen_db = typer.prompt(prompt_p1 + database_strings + prompt_p2, type=int) - 1
            selected_db_name = database_pairs[chosen_db].split(', ')[0]
            selected_db_version = database_pairs[chosen_db].split(', ')[1]
    print(selected_db_name)
    print(selected_db_version)
    return tool_version, selected_db_name, selected_db_version


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
    tool_version, database_name, database_version = get_kraken2_version_info(db)
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
        tool_version=tool_version,
        is_async=is_async,
    )
    kraken2_instance.run()


if __name__ == "__main__":
    app()

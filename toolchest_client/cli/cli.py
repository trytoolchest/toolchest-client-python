import os

import sentry_sdk
import typer

import toolchest_client as toolchest
import toolchest_client.cli.kraken2 as kraken2
import toolchest_client.cli.test as test


sentry_sdk.set_tag('send_page', False)

app = typer.Typer()

# Apparently this not recommended but it allows each tool to have its own file and maintain readability
app.command()(kraken2.kraken2)
app.command()(test.test)

if __name__ == "__main__":
    app()

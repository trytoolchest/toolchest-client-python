import os

import sentry_sdk
import typer

import kraken2
import test
import toolchest_client as toolchest

os.environ["BASE_URL"] = "https://api.toolche.st"
sentry_sdk.set_tag('send_page', False)
toolchest.set_key("ZjVhMmE.NDA1MTRhMzMtMTMyZC00YmU4LWE2NzEtZDFhYThiNzRiZGJj")

app = typer.Typer()

# Apparently this not recommended but it allows each tool to have its own file and maintain readability
app.command()(kraken2.kraken2)
app.command()(test.test)

if __name__ == "__main__":
    app()

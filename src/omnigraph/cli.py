import typer
from rich import print

from omnigraph import __version__

app = typer.Typer(
    name="omnigraph",
    help="Local knowledge graph across all your drives.",
    no_args_is_help=True,
)


def _version_callback(value: bool):
    if value:
        print(f"omnigraph {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
):
    pass


if __name__ == "__main__":
    app()

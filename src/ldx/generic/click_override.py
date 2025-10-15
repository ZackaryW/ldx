from typing import IO, Any
import click

global_echo = True

def echo(
    message: Any | None = None,
    file: IO[Any] | None = None,
    nl: bool = True,
    err: bool = False,
    color: bool | None = None
):
    """A simple wrapper around click.echo to standardize output handling."""
    if not global_echo:
        return

    click.echo(message, file=file, nl=nl, err=err, color=color)
from pathlib import Path
import sys
import click
import ldx.ldx_runner.builtins
from ldx.ldx_runner.core.runner import LDXRunner

@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, help="Enable debug mode.")
@click.pass_context
def cli(ctx : click.Context, debug: bool):
    """ldx command-line interface."""
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    ctx.obj = LDXRunner()
    ctx.ensure_object(LDXRunner)

    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())

@cli.command()
@click.argument('config_path', type=str)
def run(config_path):
    """Run LDXRunner with the specified configuration."""
    runner : LDXRunner = click.get_current_context().obj
    runner.create_instance(config_path).run()

@cli.command()
def folder():
    """Open the LDXRunner configuration folder."""
    
    Path.home().joinpath(".ldx", "runner", "configs").mkdir(parents=True, exist_ok=True)
    import os
    os.startfile(Path.home().joinpath(".ldx", "runner", "configs"))

@cli.command()
def server():
    """Run the LDX scheduler server."""
    from ldx.ldx_server.server import main
    main()

try:
    from .client import client
    cli.add_command(client)
except ImportError:
    pass


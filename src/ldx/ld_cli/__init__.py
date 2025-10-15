

import click
import logging

@click.group(invoke_without_command=True)
@click.version_option()
@click.help_option('-h', '--help')
@click.option("-np","--no-print", is_flag=True, help="Suppress all output messages.")
@click.option(
    '--ldconsole-path',
    type=click.Path(exists=True),
    required=False,
    envvar='LD_CONSOLE_PATH',
    help='Path to ldconsole.exe (auto-detected if not provided)'
)
@click.pass_context
def cli(ctx : click.Context, no_print, ldconsole_path):
    if no_print:
        import ldx.generic.click_override as click_override
        click_override.global_echo = False

    if not click.get_current_context().invoked_subcommand:
        click.echo(cli.get_help(click.get_current_context()))



    ctx.ensure_object(dict)
    if ldconsole_path:
        ctx.obj['ldconsole_path'] = ldconsole_path


from ldx.ld_cli.discover import discover # noqa E402
cli.add_command(discover)

from ldx.ld_cli.commands import cmds # noqa E402
cli.add_command(cmds)

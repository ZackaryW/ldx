

import click

@click.group(invoke_without_command=True)
@click.version_option()
@click.help_option('-h', '--help')
@click.option("--no-print", is_flag=True, help="Suppress all output messages.")
def cli(no_print):
    if no_print:
        import ldx.generic.click_override as click_override
        click_override.global_echo = False

    if not click.get_current_context().invoked_subcommand:
        click.echo(cli.get_help(click.get_current_context()))


from ldx.ld_cli.discover import discover # noqa E402
cli.add_command(discover)



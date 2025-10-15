"""App management commands (batchable)."""

import click
from ldx.ld_cli.commands.command_factory import create_batchable_command


@click.group(name='app', help='App management commands (supports batch with -bs/-bl)')
def app_group():
    """Group for app-related commands."""
    pass


# All app commands are batchable
app_commands = {
    'installapp': 'Install an APK file or app by package name on emulator instance(s)',
    'uninstallapp': 'Uninstall an app by package name from emulator instance(s)',
    'runapp': 'Run/launch an app by package name on emulator instance(s)',
    'killapp': 'Kill/stop a running app by package name on emulator instance(s)',
    'launchex': 'Launch an app with extended options on emulator instance(s)',
    'backupapp': 'Backup an app and its data from emulator instance(s)',
    'restoreapp': 'Restore an app and its data to emulator instance(s)'
}

for cmd_name, help_text in app_commands.items():
    app_group.add_command(create_batchable_command(cmd_name, help_text))

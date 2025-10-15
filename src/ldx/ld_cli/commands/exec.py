"""Execution commands (batchable operations)."""

import click
from ldx.ld_cli.commands.command_factory import create_batchable_command, create_exec_command


@click.group(name='exec', help='Execution commands (supports batch with -bs/-bl)')
def exec_group():
    """Group for execution commands."""
    pass


# Batchable commands
batchable_commands = {
    'launch': 'Launch/start an emulator instance',
    'quit': 'Quit/stop an emulator instance',
    'reboot': 'Reboot an emulator instance'
}

for cmd_name, help_text in batchable_commands.items():
    exec_group.add_command(create_batchable_command(cmd_name, help_text))


# Non-batchable exec commands
non_batchable_commands = {
    'add': 'Create a new emulator instance',
    'copy': 'Copy an existing emulator instance',
    'remove': 'Remove/delete an emulator instance',
    'rename': 'Rename an emulator instance',
    'locate': 'Set GPS location for an emulator instance',
    'adb': 'Execute an ADB command on an emulator instance',
    'setprop': 'Set a system property on an emulator instance',
    'downcpu': 'Throttle CPU usage for an emulator instance',
    'backup': 'Backup an emulator instance',
    'restore': 'Restore an emulator instance from backup',
    'action': 'Execute automated action on an emulator instance',
    'scan': 'Scan a file on an emulator instance'
}

for cmd_name, help_text in non_batchable_commands.items():
    exec_group.add_command(create_exec_command(cmd_name, help_text))


# File transfer commands (batchable)
file_commands = {
    'pull': 'Pull/download files from emulator to host',
    'push': 'Push/upload files from host to emulator'
}

for cmd_name, help_text in file_commands.items():
    exec_group.add_command(create_batchable_command(cmd_name, help_text))

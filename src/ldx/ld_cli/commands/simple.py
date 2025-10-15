"""Simple execution commands (no parameters)."""

import click
from ldx.ld_cli.commands.command_factory import create_simple_command


@click.group(name='simple', help='Simple execution commands')
def simple_group():
    """Group for simple commands that require no parameters."""
    pass


# Register all simple commands
simple_commands = {
    'rock': 'Shake the emulator window',
    'zoomOut': 'Zoom out the emulator window',
    'zoomIn': 'Zoom in the emulator window', 
    'sortWnd': 'Sort and arrange emulator windows',
    'quitall': 'Quit all running emulator instances'
}

for cmd_name, help_text in simple_commands.items():
    simple_group.add_command(create_simple_command(cmd_name, help_text))

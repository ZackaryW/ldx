"""Configuration commands (modify, globalsetting, operaterecord)."""

import click
from ldx.ld_cli.commands.command_factory import create_batchable_command, create_exec_command


@click.group(name='config', help='Configuration commands')
def config_group():
    """Group for configuration commands."""
    pass


# Batchable configuration commands
config_group.add_command(create_batchable_command(
    'modify',
    'Modify emulator instance settings (CPU, memory, resolution, device info, etc.)'
))

config_group.add_command(create_batchable_command(
    'operaterecord',
    'Execute/operate a recorded macro/script on emulator instance(s)'
))


# Global settings (not batchable, affects all instances)
config_group.add_command(create_exec_command(
    'globalsetting',
    'Configure global settings (FPS, audio, fastplay, cleanmode)'
))

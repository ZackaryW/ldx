"""Query commands (return information)."""

import click
from ldx.ld_cli.commands.command_factory import create_simple_command, create_query_command


@click.group(name='query', help='Query commands that return information')
def query_group():
    """Group for query commands."""
    pass


# Simple queries (no parameters)
simple_queries = {
    'list': 'List all emulator instances (simple format)',
    'runninglist': 'List all currently running emulator instances',
    'list2': 'List all emulator instances (detailed format with metadata)',
    
}

for cmd_name, help_text in simple_queries.items():
    query_group.add_command(create_simple_command(cmd_name, help_text))


# Queries with targeting (name/index)
target_queries = {
    'isrunning': 'Check if an emulator instance is running',
    'operatelist': 'List operations for an emulator instance',
    'list3': 'Query a single emulator instance in detailed format with metadata'
}

for cmd_name, help_text in target_queries.items():
    query_group.add_command(create_query_command(cmd_name, has_target=True, help_text=help_text))


# Queries with additional parameters
query_group.add_command(create_query_command(
    'getprop',
    has_target=True,
    help_text='Get a system property value from an emulator instance'
))

query_group.add_command(create_query_command(
    'operateinfo',
    has_target=True,
    help_text='Get operation information for an emulator instance'
))

"""Parameter definitions for CLI commands."""

import click


# Common parameters used across multiple commands
def name_option():
    """Single target by name."""
    return click.option(
        '--name', 
        type=str, 
        help='Target instance by name'
    )


def index_option():
    """Single target by index."""
    return click.option(
        '--index', 
        type=int, 
        help='Target instance by index (ID)'
    )


def batch_string_option():
    """Batch targeting by comma-separated list."""
    return click.option(
        '-bs', '--batch-string',
        type=str,
        help='Batch: comma-separated indices/names (e.g., "0,1,2" or "name1,name2")'
    )


def batch_lambda_option():
    """Batch targeting by lambda filter."""
    return click.option(
        '-bl', '--batch-lambda',
        type=str,
        help='Batch: Python lambda filter (e.g., "lambda x: x[\'id\'] < 5")'
    )


# Command-specific parameters
COMMAND_PARAMS = {
    # Simple commands with name/index
    'quit': [],
    'launch': [],
    'reboot': [],
    'remove': [],
    'isrunning': [],
    'list3': [],
    # Commands with additional parameters
    'add': [
        click.option('--name', type=str, required=True, help='Name for the new instance')
    ],
    'copy': [
        click.option('--name', type=str, required=True, help='Name for the copied instance'),
        click.option('--from', '_from', type=str, required=True, help='Source instance name to copy from')
    ],
    
    'rename': [
        click.option('--title', type=str, required=True, help='New name/title for the instance')
    ],
    
    'installapp': [
        click.option('--filename', type=str, help='Path to APK file to install'),
        click.option('--packagename', type=str, help='Package name of the app')
    ],
    
    'uninstallapp': [
        click.option('--packagename', type=str, required=True, help='Package name of the app to uninstall')
    ],
    
    'runapp': [
        click.option('--packagename', type=str, required=True, help='Package name of the app to run')
    ],
    
    'killapp': [
        click.option('--packagename', type=str, required=True, help='Package name of the app to kill')
    ],
    
    'launchex': [
        click.option('--packagename', type=str, required=True, help='Package name of the app to launch')
    ],
    
    'locate': [
        click.option('--lli', type=str, required=True, help='Location coordinates (longitude,latitude,altitude)')
    ],
    
    'adb': [
        click.option('--command', type=str, required=True, help='ADB command to execute')
    ],
    
    'setprop': [
        click.option('--key', type=str, required=True, help='Property key'),
        click.option('--value', type=str, required=True, help='Property value')
    ],
    
    'getprop': [
        click.option('--key', type=str, required=True, help='Property key to query')
    ],
    
    'downcpu': [
        click.option('--rate', type=int, required=True, help='CPU throttle rate')
    ],
    
    'backup': [
        click.option('--file', type=str, required=True, help='Backup file path')
    ],
    
    'restore': [
        click.option('--file', type=str, required=True, help='Restore file path')
    ],
    
    'action': [
        click.option('--key', type=str, required=True, help='Action key'),
        click.option('--value', type=str, required=True, help='Action value')
    ],
    
    'scan': [
        click.option('--file', type=str, required=True, help='File to scan')
    ],
    
    'pull': [
        click.option('--remote', type=str, required=True, help='Remote path in emulator'),
        click.option('--local', type=str, required=True, help='Local path on host')
    ],
    
    'push': [
        click.option('--remote', type=str, required=True, help='Remote path in emulator'),
        click.option('--local', type=str, required=True, help='Local path on host')
    ],
    
    'backupapp': [
        click.option('--packagename', type=str, required=True, help='Package name to backup'),
        click.option('--file', type=str, required=True, help='Backup file path')
    ],
    
    'restoreapp': [
        click.option('--packagename', type=str, required=True, help='Package name to restore'),
        click.option('--file', type=str, required=True, help='Restore file path')
    ],
    
    'operatelist': [],
    
    'operateinfo': [
        click.option('--file', type=str, required=True, help='Operation file path')
    ],
    
    'operaterecord': [
        click.option('--content', type=str, required=True, help='Record content as JSON string')
    ],
    
    'modify': [
        click.option('--resolution', type=str, help='Screen resolution (e.g., "1920x1080")'),
        click.option('--cpu', type=click.Choice(['1', '2', '3', '4']), help='Number of CPU cores'),
        click.option('--memory', type=click.Choice(['256', '512', '768', '1024', '2048', '4096', '8192']), 
                     help='Memory in MB'),
        click.option('--manufacturer', type=str, help='Device manufacturer name'),
        click.option('--model', type=str, help='Device model name'),
        click.option('--pnumber', type=int, help='Phone number'),
        click.option('--imei', type=str, help='IMEI number (use "auto" to generate)'),
        click.option('--imsi', type=str, help='IMSI number (use "auto" to generate)'),
        click.option('--simserial', type=str, help='SIM serial number (use "auto" to generate)'),
        click.option('--androidid', type=str, help='Android ID (use "auto" to generate)'),
        click.option('--mac', type=str, help='MAC address (use "auto" to generate)'),
        click.option('--autorotate/--no-autorotate', default=None, help='Enable/disable auto-rotation'),
        click.option('--lockwindow/--no-lockwindow', default=None, help='Enable/disable window lock'),
        click.option('--root/--no-root', default=None, help='Enable/disable root access')
    ],
    
    'globalsetting': [
        click.option('--fps', type=int, help='Frames per second setting'),
        click.option('--audio/--no-audio', default=None, help='Enable/disable audio'),
        click.option('--fastplay/--no-fastplay', default=None, help='Enable/disable fast play mode'),
        click.option('--cleanmode/--no-cleanmode', default=None, help='Enable/disable clean mode')
    ]
}

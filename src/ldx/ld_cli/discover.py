
import click
from ldx.ld_utils.discover import discover_process
from ldx.generic.click_override import echo
from ldx.ld_utils.config import LD_CONFIG, LD_CONFIG_FILE
from ldx.utils.json import save_json


@click.command()
@click.option('--dry-run', is_flag=True, help="Simulate the discovery process without making changes.")
def discover(dry_run):
    """Discover the LDPlayer installation directory by searching running processes."""
    path = discover_process()
    if not path:
        echo("LDPlayer installation directory not found.")
        return

    echo(f"LDPlayer installation directory found at: {path}")

    if dry_run:
        echo("Dry run enabled. No changes will be made.")
        return

    for config_path in LD_CONFIG["path"]:
        if config_path == str(path.absolute()):
            echo("Path already exists in configuration.")
            return

    LD_CONFIG["path"].append(str(path.absolute()))
    echo("Path added to configuration.")

    save_json(LD_CONFIG_FILE, LD_CONFIG)
    echo(f"Configuration saved to {LD_CONFIG_FILE}")
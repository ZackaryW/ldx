"""
LDX Server Client CLI

Provides command-line interface for interacting with LDX scheduler server.

Commands:
- register: Register a job from config file
- trigger: Trigger an on-demand job
- list: List jobs (running, scheduled, registry)
- status: Get job status
- cancel: Cancel a scheduled job
- unregister: Remove job from registry
"""

import click
import requests
import json
import toml
from pathlib import Path
from typing import Optional


def get_server_url(ctx: click.Context) -> str:
    """Get server URL from context or default"""
    return ctx.obj.get('server_url', 'http://localhost:5000')


def handle_response(response: requests.Response):
    """Handle API response and display results"""
    try:
        data = response.json()
        if response.status_code >= 400:
            click.secho(f"Error ({response.status_code}): {data.get('error', 'Unknown error')}", fg='red')
            if 'hint' in data:
                click.secho(f"Hint: {data['hint']}", fg='yellow')
        else:
            click.secho(json.dumps(data, indent=2), fg='green')
    except Exception as e:
        click.secho(f"Failed to parse response: {e}", fg='red')
        click.echo(response.text)


@click.group()
@click.option('--server', '-s', default='http://localhost:5000', help='Server URL')
@click.pass_context
def client(ctx, server):
    """LDX Server Client - Interact with LDX scheduler server"""
    ctx.ensure_object(dict)
    ctx.obj['server_url'] = server


@client.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--job-id', '-j', help='Job ID (default: filename without extension)')
@click.option('--replace', is_flag=True, help='Replace existing job with same ID')
@click.pass_context
def register(ctx, config_file, job_id, replace):
    """
    Register a job from a TOML config file.
    
    If config has [schedule] section, it will be scheduled automatically.
    Otherwise, it will be registered as on-demand (trigger manually).
    
    Example:
        ldx-client register my_job.toml
        ldx-client register my_job.toml --job-id custom_name
    """
    server_url = get_server_url(ctx)
    config_path = Path(config_file)
    
    # Load config
    try:
        with open(config_path, 'r') as f:
            config = toml.load(f)
    except Exception as e:
        click.secho(f"Failed to load config: {e}", fg='red')
        return
    
    # Use filename as job_id if not provided
    if not job_id:
        job_id = config_path.stem
    
    # Extract schedule if present
    schedule = config.get('schedule')
    
    # Prepare request
    payload = {
        'job_id': job_id,
        'config': config,
        'replace_existing': replace
    }
    
    if schedule:
        payload['schedule'] = schedule
    
    # Send request
    try:
        response = requests.post(
            f"{server_url}/api/scheduler/jobs",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        handle_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Request failed: {e}", fg='red')


@client.command()
@click.argument('job_id')
@click.pass_context
def trigger(ctx, job_id):
    """
    Trigger an on-demand job to run immediately.
    
    Returns the execution_id which can be used to check status.
    
    Example:
        ldx-client trigger my_job
        # Returns: {"execution_id": "my_job_20251022_145129", ...}
        ldx-client status my_job_20251022_145129
    """
    server_url = get_server_url(ctx)
    
    try:
        response = requests.post(f"{server_url}/api/scheduler/jobs/{job_id}/trigger")
        handle_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Request failed: {e}", fg='red')


@client.group()
def list():
    """List jobs, executions, or registry entries"""
    pass


@list.command('jobs')
@click.pass_context
def list_jobs(ctx):
    """
    List all jobs with their status.
    
    Example:
        ldx-client list jobs
    """
    server_url = get_server_url(ctx)
    
    try:
        response = requests.get(f"{server_url}/api/scheduler/jobs")
        handle_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Request failed: {e}", fg='red')


@list.command('active')
@click.pass_context
def list_active(ctx):
    """
    List currently running jobs.
    
    Example:
        ldx-client list active
    """
    server_url = get_server_url(ctx)
    
    try:
        response = requests.get(f"{server_url}/api/scheduler/jobs/active")
        handle_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Request failed: {e}", fg='red')


@list.command('registry')
@click.option('--type', '-t', 'filter_type', 
              type=click.Choice(['all', 'scheduled', 'on_demand']), 
              default='all',
              help='Filter registry by type')
@click.pass_context
def list_registry(ctx, filter_type):
    """
    List registered jobs.
    
    Example:
        ldx-client list registry
        ldx-client list registry --type on_demand
    """
    server_url = get_server_url(ctx)
    
    try:
        response = requests.get(
            f"{server_url}/api/scheduler/registry",
            params={'type': filter_type}
        )
        handle_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Request failed: {e}", fg='red')


@client.command()
@click.argument('job_id')
@click.pass_context
def status(ctx, job_id):
    """
    Get status of a specific job or execution.
    
    For triggered jobs, use the execution_id returned from the trigger command.
    
    Example:
        ldx-client status my_job  # For scheduled jobs
        ldx-client status my_job_20251022_145129  # For triggered executions
    """
    server_url = get_server_url(ctx)
    
    try:
        response = requests.get(f"{server_url}/api/scheduler/jobs/{job_id}")
        handle_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Request failed: {e}", fg='red')


@client.command()
@click.argument('job_id')
@click.pass_context
def cancel(ctx, job_id):
    """
    Cancel a scheduled job (cannot cancel running jobs).
    
    Example:
        ldx-client cancel my_job
    """
    server_url = get_server_url(ctx)
    
    try:
        response = requests.delete(f"{server_url}/api/scheduler/jobs/{job_id}")
        handle_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Request failed: {e}", fg='red')


@client.command()
@click.argument('job_id')
@click.pass_context
def unregister(ctx, job_id):
    """
    Remove a job from registry (also cancels if scheduled).
    
    Example:
        ldx-client unregister my_job
    """
    server_url = get_server_url(ctx)
    
    try:
        response = requests.delete(f"{server_url}/api/scheduler/registry/{job_id}")
        handle_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Request failed: {e}", fg='red')


@client.command()
@click.argument('job_id')
@click.pass_context
def info(ctx, job_id):
    """
    Get detailed info about a registered job.
    
    Example:
        ldx-client info my_job
    """
    server_url = get_server_url(ctx)
    
    try:
        response = requests.get(f"{server_url}/api/scheduler/registry/{job_id}")
        handle_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Request failed: {e}", fg='red')


@client.command()
@click.pass_context
def health(ctx):
    """
    Check server health status.
    
    Example:
        ldx-client health
    """
    server_url = get_server_url(ctx)
    
    try:
        response = requests.get(f"{server_url}/api/scheduler/health")
        handle_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Request failed: {e}", fg='red')


if __name__ == '__main__':
    client()
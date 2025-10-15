"""Factory functions for generating Click commands."""

from pprint import pformat
import click
import logging
from typing import List, Optional, Callable

from ldx.ld_cli.commands.batch_utils import (
    parse_batch_string, 
    safe_eval_lambda, 
    validate_batch_exclusivity
)
from ldx.ld_cli.commands.params import (
    name_option,
    index_option,
    batch_string_option,
    batch_lambda_option,
    COMMAND_PARAMS
)


def create_simple_command(console_method_name: str, help_text: str = None):
    """
    Create a simple command with no parameters.
    
    Args:
        console_method_name: Name of the method on Console class
        help_text: Help text for the command
        
    Returns:
        Click command function
    """
    command_name = console_method_name.replace('_', '-').lower()
    
    @click.command(name=command_name, help=help_text or f"Execute {console_method_name} command")
    @click.pass_context
    def command(ctx):
        console = ctx.obj['console']
        method = getattr(console, console_method_name)
        result = method()
        
        if not result:
            return 
        if isinstance(result, str):
            click.echo(result)
        elif isinstance(result, dict):
            click.echo(pformat(result))

        elif isinstance(result, list):
            for item in result:
                click.echo(item)
            
    return command


def create_query_command(console_method_name: str, has_target: bool = False, help_text: str = None):
    """
    Create a query command that returns output.
    
    Args:
        console_method_name: Name of the method on Console class
        has_target: Whether command requires name/index targeting
        help_text: Help text for the command
        
    Returns:
        Click command function
    """
    command_name = console_method_name.replace('_', '-').lower()
    
    # Get additional parameters for this command
    extra_params = COMMAND_PARAMS.get(console_method_name, [])
    
    def decorator(func):
        # Add extra parameters first
        for param in reversed(extra_params):
            func = param(func)
        
        # Add target parameters if needed
        if has_target:
            func = index_option()(func)
            func = name_option()(func)
            
        func = click.pass_context(func)
        func = click.command(name=command_name, help=help_text or f"Query {console_method_name}")(func)
        return func
    
    @decorator
    def command(ctx, name=None, index=None, **kwargs):
        console = ctx.obj['console']
        method = getattr(console, console_method_name)
        
        # Build arguments
        call_kwargs = {}
        if has_target:
            if name:
                call_kwargs['name'] = name
            elif index is not None:
                call_kwargs['index'] = index
        
        # Add extra parameters
        call_kwargs.update(kwargs)
        
        # Execute query
        result = method(**call_kwargs)
        
        # Output result
        if result:
            click.echo(result)
    
    return command


def create_batchable_command(console_method_name: str, help_text: str = None):
    """
    Create a command that supports both single and batch execution.
    
    Args:
        console_method_name: Name of the method on Console class
        help_text: Help text for the command
        
    Returns:
        Click command function
    """
    command_name = console_method_name.replace('_', '-').lower()
    
    # Get additional parameters for this command
    extra_params = COMMAND_PARAMS.get(console_method_name, [])
    
    def decorator(func):
        # Add extra parameters first
        for param in reversed(extra_params):
            func = param(func)
        
        # Add batch and targeting options
        func = batch_lambda_option()(func)
        func = batch_string_option()(func)
        func = index_option()(func)
        func = name_option()(func)
        func = click.pass_context(func)
        func = click.command(
            name=command_name, 
            help=help_text or f"Execute {console_method_name} (supports batch with -bs/-bl)"
        )(func)
        return func
    
    @decorator
    def command(ctx, name, index, batch_string, batch_lambda, **kwargs):
        console = ctx.obj['console']
        method = getattr(console, console_method_name)
        
        # Validate mutual exclusivity
        try:
            validate_batch_exclusivity(name, index, batch_string, batch_lambda)
        except ValueError as e:
            raise click.UsageError(str(e))
        
        # Batch mode
        if batch_string or batch_lambda:
            if batch_string:
                # Parse batch string: "0,1,2" or "name1,name2"
                targets = parse_batch_string(batch_string)
                logging.info(f"Executing {console_method_name} on batch targets: {targets}")
                result = method(targets, **kwargs)
            else:
                # Evaluate lambda filter
                try:
                    filter_func = safe_eval_lambda(batch_lambda)
                    logging.info(f"Executing {console_method_name} with lambda filter")
                    result = method(instances=filter_func, **kwargs)
                except (ValueError, SyntaxError) as e:
                    raise click.UsageError(f"Invalid lambda expression: {e}")
            
            # Output batch results
            if result:
                click.echo(f"Batch execution completed. Results: {result}")
        
        # Single mode
        else:
            if not name and index is None:
                raise click.UsageError(
                    f"Command '{command_name}' requires one of: "
                    "--name, --index, -bs/--batch-string, or -bl/--batch-lambda"
                )
            
            # Execute single
            call_kwargs = kwargs.copy()
            if name:
                call_kwargs['name'] = name
            elif index is not None:
                call_kwargs['index'] = index
                
            logging.info(f"Executing {console_method_name} on single target")
            result = method(**call_kwargs)
            
            # Output result
            if result:
                click.echo(result)
    
    return command


def create_exec_command(console_method_name: str, help_text: str = None):
    """
    Create a non-batchable execution command with name/index targeting.
    
    Args:
        console_method_name: Name of the method on Console class
        help_text: Help text for the command
        
    Returns:
        Click command function
    """
    command_name = console_method_name.replace('_', '-').lower()
    
    # Get additional parameters for this command
    extra_params = COMMAND_PARAMS.get(console_method_name, [])
    
    def decorator(func):
        # Add extra parameters first
        for param in reversed(extra_params):
            func = param(func)
        
        # Add targeting options if needed
        if console_method_name not in ['add', 'globalsetting']:
            func = index_option()(func)
            func = name_option()(func)
            
        func = click.pass_context(func)
        func = click.command(name=command_name, help=help_text or f"Execute {console_method_name}")(func)
        return func
    
    @decorator
    def command(ctx, name=None, index=None, **kwargs):
        console = ctx.obj['console']
        method = getattr(console, console_method_name)
        
        # Build arguments
        call_kwargs = kwargs.copy()
        
        # Handle commands that don't need name/index
        if console_method_name in ['add', 'globalsetting']:
            pass
        else:
            if name:
                call_kwargs['name'] = name
            elif index is not None:
                call_kwargs['index'] = index
            else:
                raise click.UsageError(
                    f"Command '{command_name}' requires either --name or --index"
                )
        
        # Execute
        logging.info(f"Executing {console_method_name}")
        result = method(**call_kwargs)
        
        # Output result
        if result:
            click.echo(result)
        else:
            click.echo(f"✓ Command '{command_name}' executed successfully")
    
    return command

import logging
import typing
import time
from typing import Callable, List, Union, Any

from ldx.ld_base.model_list2meta import List2Meta


def batch_execute(
    console: Any,
    command_name: str,
    targets: Union[
        List[int], 
        List[str], 
        Callable[['List2Meta'], bool],
        None
    ] = None,
    instances: Callable[['List2Meta'], bool] = None,
    console_func: Callable[[Any], Any] = None,
    *args, 
    **kwargs
):
    """
    Execute a command on multiple instances in batch.
    
    Args:
        console: The Console instance to use for execution
        command_name: Name of the command to execute
        targets: List of indices, names, or None
        instances: Lambda function to filter instances from list2 
        console_func: Lambda function that receives console and executes custom logic
        *args, **kwargs: Additional arguments to pass to the command
        
    Usage examples:
        # Execute on specific indices
        batch_execute(console, 'launch', [1, 2, 3, 4])
        
        # Execute on specific names  
        batch_execute(console, 'launch', ["xxx", "xxx2"])
        
        # Execute on filtered instances
        batch_execute(console, 'launch', instances=lambda x: x.name.startswith('test'))
        
        # Custom console execution
        batch_execute(console, 'launch', console_func=lambda c: c.launch(name='specific'))
    """
    
    # If console_func is provided, execute it directly
    if console_func is not None:
        logging.info(f"Executing batch command '{command_name}' with custom console function")
        return console_func(console)
    
    # Get the command method from console
    if not hasattr(console, command_name):
        raise ValueError(f"Command '{command_name}' not found on console")
    
    command_method = getattr(console, command_name)
    
    # If instances filter is provided, get list2 and filter
    if instances is not None:
        logging.info(f"Filtering instances for batch command '{command_name}'")
        list2_data = console.list2()
        filtered_instances = [item for item in list2_data if instances(item)]
        targets = [item["id"] for item in filtered_instances]
        logging.info(f"Found {len(targets)} instances matching filter")
    
    # If no targets specified, raise error
    if targets is None:
        raise ValueError("Either targets list, instances filter, or console_func must be provided")
    
    # Execute command for each target
    results = []
    interval = getattr(console.attr, 'interval_between_batches', -1)
    
    for i, target in enumerate(targets):
        try:
            if isinstance(target, int):
                logging.info(f"Executing '{command_name}' on index {target}")
                result = command_method(index=target, *args, **kwargs)
            elif isinstance(target, str):
                logging.info(f"Executing '{command_name}' on name '{target}'")
                result = command_method(name=target, *args, **kwargs)
            else:
                logging.warning(f"Skipping invalid target: {target}")
                continue
                
            results.append(result)
            
            # Add interval delay if specified and not negative, and not the last iteration
            if interval > 0 and i < len(targets) - 1:
                logging.info(f"Waiting {interval} seconds before next batch operation...")
                time.sleep(interval)
            
        except Exception as e:
            logging.error(f"Error executing '{command_name}' on target {target}: {e}")
            results.append(e)
    
    return results


class BatchMixin:
    """Mixin class to add batch processing capabilities to Console"""
    
    def _is_batch_call(self, args, kwargs) -> bool:
        """Check if this is a batch call based on arguments"""
        # Check if first argument is a list
        if len(args) > 0 and isinstance(args[0], list):
            return True
            
        # Check for batch-specific keyword arguments
        if 'instances' in kwargs or 'console_func' in kwargs:
            return True
            
        return False
    
    def _execute_batch(self, command_name: str, *args, **kwargs):
        """Execute a command in batch mode"""
        targets = None
        instances = kwargs.pop('instances', None)
        console_func = kwargs.pop('console_func', None)
        
        # If first argument is a list, use it as targets
        if len(args) > 0 and isinstance(args[0], list):
            targets = args[0]
            args = args[1:]  # Remove the list from args
        
        return batch_execute(
            console=self,
            command_name=command_name,
            targets=targets,
            instances=instances,
            console_func=console_func,
            *args,
            **kwargs
        )

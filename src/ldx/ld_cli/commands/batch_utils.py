"""Utilities for batch command processing in CLI."""

import ast
import logging
from typing import List, Union, Callable


def parse_batch_string(batch_str: str) -> List[Union[int, str]]:
    """
    Parse a comma-separated batch string into a list of targets.
    
    Automatically detects whether items are numeric indices or string names.
    
    Args:
        batch_str: Comma-separated string like "0,1,2" or "name1,name2"
        
    Returns:
        List of integers or strings representing target instances
        
    Examples:
        >>> parse_batch_string("0,1,2")
        [0, 1, 2]
        >>> parse_batch_string("instance1,instance2")
        ['instance1', 'instance2']
        >>> parse_batch_string("0, test, 5")
        [0, 'test', 5]
    """
    items = [s.strip() for s in batch_str.split(',')]
    result = []
    
    for item in items:
        # Try to convert to int, otherwise keep as string
        if item.isdigit():
            result.append(int(item))
        else:
            result.append(item)
    
    logging.debug(f"Parsed batch string '{batch_str}' -> {result}")
    return result


def safe_eval_lambda(lambda_str: str) -> Callable:
    """
    Safely evaluate a lambda expression string.
    
    Only allows lambda expressions, not arbitrary Python code.
    Provides basic protection against code injection.
    
    Args:
        lambda_str: String containing a lambda expression
        
    Returns:
        The evaluated lambda function
        
    Raises:
        ValueError: If the string is not a valid lambda expression
        SyntaxError: If the lambda syntax is invalid
        
    Examples:
        >>> func = safe_eval_lambda("lambda x: x['id'] < 5")
        >>> func({'id': 3})
        True
        >>> func = safe_eval_lambda("lambda x: x['name'].startswith('test')")
    """
    # Parse the expression
    try:
        tree = ast.parse(lambda_str, mode='eval')
    except SyntaxError as e:
        raise SyntaxError(f"Invalid lambda syntax: {e}")
    
    # Verify it's a lambda expression
    if not isinstance(tree.body, ast.Lambda):
        raise ValueError(
            "Only lambda expressions are allowed. "
            f"Got: {ast.dump(tree.body)}"
        )
    
    # Evaluate the lambda
    try:
        func = eval(lambda_str)
        logging.debug(f"Evaluated lambda: {lambda_str}")
        return func
    except Exception as e:
        raise ValueError(f"Failed to evaluate lambda: {e}")


def validate_batch_exclusivity(name, index, batch_string, batch_lambda):
    """
    Validate that batch options are mutually exclusive with single-target options.
    
    Args:
        name: Single target name
        index: Single target index
        batch_string: Batch string option
        batch_lambda: Batch lambda option
        
    Raises:
        ValueError: If conflicting options are provided
    """
    single_count = sum([name is not None, index is not None])
    batch_count = sum([batch_string is not None, batch_lambda is not None])
    
    if single_count > 1:
        raise ValueError("Cannot specify both --name and --index")
    
    if batch_count > 1:
        raise ValueError("Cannot specify both -bs/--batch-string and -bl/--batch-lambda")
    
    if single_count > 0 and batch_count > 0:
        raise ValueError(
            "Cannot mix single-target options (--name, --index) "
            "with batch options (-bs, -bl)"
        )

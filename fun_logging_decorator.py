from functools import wraps
from fun_logging import *

def log_function_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Log function call with arguments
        logger.debug(f":----> {func.__name__} called with args: {args} and kwargs: {kwargs}")
        
        # Execute the function
        result = func(*args, **kwargs)
        
        # Log internal values if needed (can add specific logs inside your function as well)
        # Example: logger.debug(f"Internal value in {func.__name__}: {some_internal_value}")
        
        # Log the result
        logger.debug(f"<----: {func.__name__} returned : {result}")
        
        return result
    return wrapper

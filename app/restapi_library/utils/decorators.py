import functools
import time
from typing import Any, Callable, Optional
from ..core.exceptions import RetryExhaustedError

# won't use it yet
def rate_limit(calls_per_second: float):
    """Rate limiting decorator"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

def cache_result(ttl: int = 3600):
    """Cache function result decorator"""
    cache = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(hash((args, tuple(sorted(kwargs.items())))))
            
            # Check cache
            if key in cache:
                cached_time, cached_result = cache[key]
                if time.time() - cached_time < ttl:
                    return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[key] = (time.time(), result)
            return result
        return wrapper
    return decorator
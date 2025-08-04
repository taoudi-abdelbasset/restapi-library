import time
import random
from typing import Callable, Any, Dict, Optional
from ..core.exceptions import RetryExhaustedError

class RetryHandler:
    """Handle retry logic with exponential backoff"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, 
                 backoff_factor: float = 2.0, jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
    
    def execute_with_retry(self, func: Callable, on_retry: Optional[Callable] = None, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_attempts - 1:
                    break
                
                delay = self._calculate_delay(attempt)
                
                # Call retry callback if provided
                if on_retry:
                    on_retry(attempt + 1, self.max_attempts, delay, e)
                
                time.sleep(delay)
        
        raise RetryExhaustedError(f"Max retry attempts ({self.max_attempts}) exceeded") from last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter"""
        delay = self.base_delay * (self.backoff_factor ** attempt)
        
        if self.jitter:
            delay += random.uniform(0, delay * 0.1)
        
        return delay
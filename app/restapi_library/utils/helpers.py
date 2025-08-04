import hashlib
import json
from typing import Any, Dict
from urllib.parse import urljoin

def generate_cache_key(*args: Any) -> str:
    """Generate cache key from arguments"""
    key_string = json.dumps(args, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()

def safe_join_url(base_url: str, path: str) -> str:
    """Safely join base URL with path"""
    if path.startswith('http'):
        return path
    return urljoin(base_url.rstrip('/') + '/', path.lstrip('/'))

def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result

def mask_sensitive_data(data: Any, sensitive_keys: set = None) -> Any:
    """Mask sensitive data in dictionary or string"""
    if sensitive_keys is None:
        sensitive_keys = {
            'password', 'token', 'secret', 'key', 'auth', 'authorization',
            'api_key', 'apikey', 'bearer', 'basic', 'credential'
        }
    
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                masked[key] = '[MASKED]'
            else:
                masked[key] = mask_sensitive_data(value, sensitive_keys)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item, sensitive_keys) for item in data]
    else:
        return data
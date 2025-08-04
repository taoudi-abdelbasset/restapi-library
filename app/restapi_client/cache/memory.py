import time
from typing import Any, Optional, Dict
from .base import BaseCache

class MemoryCache(BaseCache):
    """In-memory cache implementation"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Check expiration
        if entry.get('expires_at') and time.time() > entry['expires_at']:
            del self._cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL"""
        entry = {'value': value}
        
        if ttl:
            entry['expires_at'] = time.time() + ttl
        
        self._cache[key] = entry
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self._cache.pop(key, None)
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        return self.get(key) is not None
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
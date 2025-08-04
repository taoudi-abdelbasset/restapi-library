from abc import ABC, abstractmethod
from typing import Any, Optional

# library: restapi_client.cache.base
# This module defines the base cache interface for the REST API client(tokens, data, etc...).
class BaseCache(ABC):
    """Base cache interface"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries"""
        pass
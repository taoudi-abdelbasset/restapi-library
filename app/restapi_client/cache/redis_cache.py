import json
import time
from typing import Any, Optional
from .base import BaseCache
from ..core.exceptions import CacheError

# check if redis is available in the environment
# if not, raise an error when trying to use RedisCache
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class RedisCache(BaseCache):
    """Redis cache implementation"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: Optional[str] = None,
                 key_prefix: str = 'restapi:', **kwargs):
        if not REDIS_AVAILABLE:
            raise CacheError("Redis not available. Please install redis: pip install redis")
        
        self.key_prefix = key_prefix
        try:
            self.redis_client = redis.Redis(
                host=host, port=port, db=db, 
                password=password, decode_responses=True,
                **kwargs
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            raise CacheError(f"Failed to connect to Redis: {e}")
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key"""
        return f"{self.key_prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(self._make_key(key))
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            raise CacheError(f"Failed to get key '{key}' from Redis: {e}")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL"""
        try:
            serialized_value = json.dumps(value, default=str)
            redis_key = self._make_key(key)
            
            if ttl:
                self.redis_client.setex(redis_key, ttl, serialized_value)
            else:
                self.redis_client.set(redis_key, serialized_value)
        except Exception as e:
            raise CacheError(f"Failed to set key '{key}' in Redis: {e}")
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        try:
            self.redis_client.delete(self._make_key(key))
        except Exception as e:
            raise CacheError(f"Failed to delete key '{key}' from Redis: {e}")
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.redis_client.exists(self._make_key(key)))
        except Exception as e:
            raise CacheError(f"Failed to check key '{key}' in Redis: {e}")
    
    def clear(self) -> None:
        """Clear all cache entries with prefix"""
        try:
            keys = self.redis_client.keys(f"{self.key_prefix}*")
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            raise CacheError(f"Failed to clear Redis cache: {e}")
from typing import Dict, Any, Optional
from .base import BaseCache
from .memory import MemoryCache
from .redis_cache import RedisCache
from ..core.types import CacheType
from ..core.exceptions import ConfigurationError

class CacheFactory:
    """Factory for creating cache instances"""
    
    _redis_config: Optional[Dict[str, Any]] = None
    _global_cache_instances: Dict[str, BaseCache] = {}
    
    @classmethod
    def set_redis_config(cls, redis_config: Dict[str, Any]) -> None:
        """Set global Redis configuration"""
        cls._redis_config = redis_config
    
    @classmethod
    def create_cache(cls, cache_config: Dict[str, Any], 
                    cache_key: Optional[str] = None) -> BaseCache:
        """Create cache instance"""
        cache_type = CacheType(cache_config.get('type', 'memory'))
        
        # Use global cache instance if cache_key is provided
        if cache_key and cache_key in cls._global_cache_instances:
            return cls._global_cache_instances[cache_key]
        
        if cache_type == CacheType.MEMORY:
            cache_instance = MemoryCache()
        
        elif cache_type == CacheType.REDIS:
            if cls._redis_config is None:
                raise ConfigurationError(
                    "Redis configuration not set. Use RestAPILibrary.set_redis_config()"
                )
            
            # Merge cache config with global redis config
            redis_config = {**cls._redis_config, **cache_config.get('redis_config', {})}
            cache_instance = RedisCache(**redis_config)
        
        else:
            raise ConfigurationError(f"Unsupported cache type: {cache_type}")
        
        # Store global cache instance
        if cache_key:
            cls._global_cache_instances[cache_key] = cache_instance
        
        return cache_instance
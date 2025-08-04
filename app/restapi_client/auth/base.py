from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..cache.base import BaseCache
from ..core.types import TokenInfo

class BaseAuthHandler(ABC):
    """Base authentication handler"""
    
    def __init__(self, config: Dict[str, Any], cache: Optional[BaseCache] = None):
        self.config = config
        self.cache = cache
        self.cache_key_prefix = f"auth_{config.get('type', 'unknown')}_"
    
    @abstractmethod
    def apply_auth(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply authentication to request"""
        pass
    
    @abstractmethod
    def refresh_token(self) -> bool:
        """Refresh authentication token if needed"""
        pass
    
    def is_token_expired(self) -> bool:
        """Check if token is expired"""
        return False
    
    def get_cached_token(self, cache_key: str) -> Optional[TokenInfo]:
        """Get cached token"""
        if not self.cache:
            return None
        
        token_data = self.cache.get(f"{self.cache_key_prefix}{cache_key}")
        if token_data:
            return TokenInfo(**token_data)
        return None
    
    def cache_token(self, cache_key: str, token_info: TokenInfo, ttl: Optional[int] = None) -> None:
        """Cache token"""
        if not self.cache:
            return
        
        token_dict = {
            'access_token': token_info.access_token,
            'refresh_token': token_info.refresh_token,
            'expires_at': token_info.expires_at,
            'token_type': token_info.token_type
        }
        
        self.cache.set(f"{self.cache_key_prefix}{cache_key}", token_dict, ttl)
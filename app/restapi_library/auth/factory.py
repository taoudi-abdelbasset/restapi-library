from typing import Dict, Any, Optional
from .base import BaseAuthHandler
from .handlers import BearerAuthHandler, BasicAuthHandler, APIKeyAuthHandler
from .dynamic_token import DynamicTokenAuthHandler
from ..core.types import AuthType
from ..core.exceptions import ConfigurationError
from ..cache.base import BaseCache

class AuthFactory:
    """Factory for creating authentication handlers"""
    
    _handlers = {
        AuthType.BEARER: BearerAuthHandler,
        AuthType.BASIC: BasicAuthHandler,
        AuthType.API_KEY: APIKeyAuthHandler,
        AuthType.DYNAMIC_TOKEN: DynamicTokenAuthHandler,
    }
    
    @classmethod
    def create_handler(cls, auth_config: Dict[str, Any], 
                      cache: Optional[BaseCache] = None,
                      base_url: Optional[str] = None) -> BaseAuthHandler:
        """Create authentication handler"""
        auth_type = AuthType(auth_config['type'])
        
        if auth_type not in cls._handlers:
            raise ConfigurationError(f"Unsupported auth type: {auth_type}")
        
        handler_class = cls._handlers[auth_type]
        
        # For dynamic token auth, resolve full URLs
        if auth_type == AuthType.DYNAMIC_TOKEN and base_url:
            auth_config = cls._resolve_dynamic_token_urls(auth_config, base_url)
        
        return handler_class(auth_config, cache)
    
    @classmethod
    def _resolve_dynamic_token_urls(cls, auth_config: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        """Resolve relative URLs for dynamic token endpoints"""
        config = auth_config.copy()
        
        # Resolve login endpoint URL
        if 'login_endpoint' in config:
            login_path = config['login_endpoint']['path']
            if not login_path.startswith('http'):
                config['login_endpoint']['path'] = f"{base_url.rstrip('/')}{login_path}"
        
        # Resolve refresh endpoint URL
        if 'refresh_endpoint' in config:
            refresh_path = config['refresh_endpoint']['path']
            if not refresh_path.startswith('http'):
                config['refresh_endpoint']['path'] = f"{base_url.rstrip('/')}{refresh_path}"
        
        return config
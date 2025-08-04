import time
import requests
from typing import Dict, Any, Optional
from .base import BaseAuthHandler
from ..core.types import TokenInfo, TokenPlacementType
from ..core.exceptions import AuthenticationError
from ..cache.base import BaseCache

class DynamicTokenAuthHandler(BaseAuthHandler):
    """Dynamic token authentication with automatic refresh"""
    
    def __init__(self, config: Dict[str, Any], cache: Optional[BaseCache] = None):
        super().__init__(config, cache)
        
        self.login_endpoint = config['login_endpoint']
        self.token_placement = config.get('token_placement', {})
        self.refresh_endpoint = config.get('refresh_endpoint')
        
        # Extract field names
        self.token_field = self.login_endpoint.get('token_field', 'access_token')
        self.refresh_token_field = self.login_endpoint.get('refresh_token_field', 'refresh_token')
        self.expires_in_field = self.login_endpoint.get('expires_in_field', 'expires_in')
        
        # Cache configuration
        self.cache_ttl = config.get('cache', {}).get('ttl', 3600)
        self.cache_key = f"token_{hash(str(config))}"
        
        # Current token info
        self._current_token: Optional[TokenInfo] = None
        self._load_cached_token()
    
    def _load_cached_token(self) -> None:
        """Load token from cache"""
        if self.cache:
            self._current_token = self.get_cached_token(self.cache_key)
    
    def apply_auth(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply authentication to request"""
        # Get valid token
        token = self._get_valid_token()
        if not token:
            raise AuthenticationError("Failed to obtain valid token")
        
        # Apply token based on placement configuration
        placement_type = TokenPlacementType(
            self.token_placement.get('type', 'header')
        )
        
        if placement_type == TokenPlacementType.HEADER:
            headers = request_kwargs.get('headers', {})
            header_name = self.token_placement.get('header_name', 'Authorization')
            prefix = self.token_placement.get('prefix', 'Bearer')
            
            if prefix:
                headers[header_name] = f"{prefix} {token.access_token}"
            else:
                headers[header_name] = token.access_token
            
            request_kwargs['headers'] = headers
        
        elif placement_type == TokenPlacementType.QUERY:
            params = request_kwargs.get('params', {})
            query_param = self.token_placement.get('param_name', 'access_token')
            params[query_param] = token.access_token
            request_kwargs['params'] = params
        
        elif placement_type == TokenPlacementType.BODY:
            json_data = request_kwargs.get('json', {})
            body_field = self.token_placement.get('field_name', 'access_token')
            json_data[body_field] = token.access_token
            request_kwargs['json'] = json_data
        
        return request_kwargs
    
    def _get_valid_token(self) -> Optional[TokenInfo]:
        """Get valid token, refresh if needed"""
        # Check if current token is valid
        if self._current_token and not self.is_token_expired():
            return self._current_token
        
        # Try to refresh token
        if self._current_token and self._current_token.refresh_token and self.refresh_endpoint:
            if self._refresh_token():
                return self._current_token
        
        # Login to get new token
        if self._login():
            return self._current_token
        
        return None
    
    def is_token_expired(self) -> bool:
        """Check if token is expired"""
        if not self._current_token or not self._current_token.expires_at:
            return True
        
        # Add 60 second buffer
        return time.time() >= (self._current_token.expires_at - 60)
    
    def _login(self) -> bool:
        """Perform login to get new token"""
        try:
            login_config = self.login_endpoint
            
            # Prepare login request
            login_url = login_config['path']  # Should be full URL or will be resolved by base_url
            login_method = login_config['method']
            login_body = login_config.get('body', {})
            
            # Make login request
            response = requests.request(
                method=login_method,
                url=login_url,
                json=login_body,
                timeout=30
            )
            
            if not response.ok:
                raise AuthenticationError(f"Login failed with status {response.status_code}")
            
            token_data = response.json()
            
            # Extract token information
            access_token = token_data.get(self.token_field)
            if not access_token:
                raise AuthenticationError(f"Token field '{self.token_field}' not found in response")
            
            refresh_token = token_data.get(self.refresh_token_field)
            expires_in = token_data.get(self.expires_in_field)
            
            # Calculate expiration time
            expires_at = None
            if expires_in:
                expires_at = time.time() + int(expires_in)
            
            # Create token info
            self._current_token = TokenInfo(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                token_type=self.token_placement.get('prefix', 'Bearer')
            )
            
            # Cache token
            if self.cache:
                cache_ttl = min(expires_in, self.cache_ttl) if expires_in else self.cache_ttl
                self.cache_token(self.cache_key, self._current_token, cache_ttl)
            
            return True
            
        except Exception as e:
            raise AuthenticationError(f"Login failed: {e}")
    
    def _refresh_token(self) -> bool:
        """Refresh token using refresh token"""
        if not self.refresh_endpoint or not self._current_token or not self._current_token.refresh_token:
            return False
        
        try:
            refresh_config = self.refresh_endpoint
            
            # Prepare refresh request
            refresh_url = refresh_config['path']
            refresh_method = refresh_config['method']
            body_field = refresh_config.get('body_field', 'refresh_token')
            
            refresh_body = {body_field: self._current_token.refresh_token}
            
            # Make refresh request
            response = requests.request(
                method=refresh_method,
                url=refresh_url,
                json=refresh_body,
                timeout=30
            )
            
            if not response.ok:
                return False
            
            token_data = response.json()
            
            # Update token information
            access_token = token_data.get(self.token_field)
            if access_token:
                self._current_token.access_token = access_token
            
            # Update refresh token if provided
            new_refresh_token = token_data.get(self.refresh_token_field)
            if new_refresh_token:
                self._current_token.refresh_token = new_refresh_token
            
            # Update expiration
            expires_in = token_data.get(self.expires_in_field)
            if expires_in:
                self._current_token.expires_at = time.time() + int(expires_in)
            
            # Cache updated token
            if self.cache:
                cache_ttl = min(expires_in, self.cache_ttl) if expires_in else self.cache_ttl
                self.cache_token(self.cache_key, self._current_token, cache_ttl)
            
            return True
            
        except Exception:
            return False
    
    def refresh_token(self) -> bool:
        """Public method to refresh token"""
        return self._refresh_token() or self._login()
import base64
from typing import Dict, Any, Optional
from .base import BaseAuthHandler

class BearerAuthHandler(BaseAuthHandler):
    """Bearer token authentication"""
    
    def apply_auth(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        headers = request_kwargs.get('headers', {})
        headers['Authorization'] = f"Bearer {self.config['token']}"
        request_kwargs['headers'] = headers
        return request_kwargs
    
    def refresh_token(self) -> bool:
        return True

class BasicAuthHandler(BaseAuthHandler):
    """Basic authentication"""
    
    def apply_auth(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        username = self.config['username']
        password = self.config['password']
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        
        headers = request_kwargs.get('headers', {})
        headers['Authorization'] = f"Basic {credentials}"
        request_kwargs['headers'] = headers
        return request_kwargs
    
    def refresh_token(self) -> bool:
        return True

class APIKeyAuthHandler(BaseAuthHandler):
    """API Key authentication"""
    
    def apply_auth(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        key_name = self.config.get('key_name', 'X-API-Key')
        api_key = self.config['api_key']
        location = self.config.get('location', 'header')
        
        if location == 'header':
            headers = request_kwargs.get('headers', {})
            headers[key_name] = api_key
            request_kwargs['headers'] = headers
        elif location == 'query':
            params = request_kwargs.get('params', {})
            params[key_name] = api_key
            request_kwargs['params'] = params
        
        return request_kwargs
    
    def refresh_token(self) -> bool:
        return True
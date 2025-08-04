import time
from typing import Dict, Any, Optional, Union, Callable
from ..models.response import APIResponse
from ..utils.validation import Validator
from ..core.exceptions import ValidationError
from ..models.registry import ModelRegistry
from ..utils.helpers import generate_cache_key

class APIEndpoint:
    """Represents a single API endpoint with enhanced features"""
    
    def __init__(self, client: 'APIClient', endpoint_name: str, endpoint_config: Dict[str, Any]):
        self.client = client
        self.name = endpoint_name
        self.config = endpoint_config
        self.path = endpoint_config['path']
        self.method = endpoint_config['method']
        self.auth_required = endpoint_config.get('auth_required', False)
        self.raise_on_error = endpoint_config.get('raise_on_error', True)
        self.retry_config = endpoint_config.get('retry', {})
        self.timeout = endpoint_config.get('timeout', 30)
        
        # Model configurations
        self.request_model = endpoint_config.get('request_model')
        self.response_model = endpoint_config.get('response_model')
        self.body_required = endpoint_config.get('body_required', False)
        
        # Parameter configuration
        self.params_config = endpoint_config.get('params', {})
        
        # Caching configuration
        self.cache_config = endpoint_config.get('cache', {})
        self.cache_enabled = self.cache_config.get('enabled', False)
        self.cache_ttl = self.cache_config.get('ttl', 3600)
        
        # Response transformation
        self.response_transform = endpoint_config.get('response_transform')
        
        # Custom middleware
        self._middleware: list = []
    
    def __call__(self, **kwargs) -> Union[APIResponse, Dict[str, Any], Any]:
        """Execute the endpoint"""
        # Check cache first
        if self.cache_enabled and self.method == 'GET':
            cache_key = self._generate_cache_key(**kwargs)
            cached_result = self._get_cached_response(cache_key)
            if cached_result is not None:
                return cached_result
        
        # Execute endpoint
        result = self.client._execute_endpoint(self, **kwargs)
        
        # Cache result if enabled
        if self.cache_enabled and self.method == 'GET':
            cache_key = self._generate_cache_key(**kwargs)
            self._cache_response(cache_key, result)
        
        # Apply response transformation
        if self.response_transform and callable(self.response_transform):
            result = self.response_transform(result)
        
        return result
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware function"""
        self._middleware.append(middleware)
    
    def _generate_cache_key(self, **kwargs) -> str:
        """Generate cache key for request"""
        return generate_cache_key(
            self.client.api_name,
            self.name,
            kwargs.get('params', {}),
            kwargs.get('headers', {})
        )
    
    def _get_cached_response(self, cache_key: str) -> Optional[Any]:
        """Get cached response"""
        if self.client.cache:
            return self.client.cache.get(f"endpoint_{cache_key}")
        return None
    
    def _cache_response(self, cache_key: str, response: Any) -> None:
        """Cache response"""
        if self.client.cache:
            self.client.cache.set(f"endpoint_{cache_key}", response, self.cache_ttl)
    
    def validate_and_prepare_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and prepare parameters"""
        if self.params_config:
            return Validator.validate_params(params, self.params_config)
        return params
    
    def validate_and_prepare_body(self, body: Any) -> Any:
        """Validate and prepare request body"""
        if self.body_required and body is None:
            raise ValidationError(f"Body is required for endpoint '{self.name}'")
        
        if body is not None and self.request_model:
            model_class = ModelRegistry.get_model(self.request_model)
            
            if model_class:
                if not isinstance(body, model_class):
                    try:
                        body = ModelRegistry.create_instance(self.request_model, body)
                    except Exception as e:
                        raise ValidationError(f"Invalid body format for model '{self.request_model}': {e}")
                
                if hasattr(body, 'validate') and not body.validate():
                    raise ValidationError(f"Body validation failed for model '{self.request_model}'")
        
        return body
import time
import requests
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin
from .config import ConfigParser
from .endpoint import APIEndpoint
from ..auth.factory import AuthFactory
from ..cache.factory import CacheFactory
from ..utils.retry import RetryHandler
from ..utils.logging import APILogger
from ..core.exceptions import APIError, AuthenticationError
from ..models.response import APIResponse
from ..models.registry import ModelRegistry

class APIClient:
    """Main API client class"""
    
    def __init__(self, api_name: str, config_parser: ConfigParser, 
                 logger: Optional[APILogger] = None):
        self.api_name = api_name
        self.config_parser = config_parser
        self.api_config = config_parser.get_api_config(api_name)
        
        # Initialize components
        self.base_url = self.api_config['base_url']
        self.default_version = self.api_config.get('default_version', 'v1')
        self.session = requests.Session()
        
        # Initialize logging
        self.logger = logger or APILogger(
            log_requests=self.api_config.get('logging', {}).get('log_requests', True),
            log_responses=self.api_config.get('logging', {}).get('log_responses', True),
            log_sensitive_data=self.api_config.get('logging', {}).get('log_sensitive_data', False)
        )
        
        # Initialize cache if needed
        self.cache = None
        if 'auth' in self.api_config and 'cache' in self.api_config['auth']:
            cache_config = self.api_config['auth']['cache']
            self.cache = CacheFactory.create_cache(cache_config, f"auth_{api_name}")
        
        # Setup authentication
        self.auth_handler = None
        if 'auth' in self.api_config:
            self.auth_handler = AuthFactory.create_handler(
                self.api_config['auth'], 
                self.cache,
                self.base_url
            )
            self.logger.log_auth_event(
                api_name, 
                self.api_config['auth']['type'], 
                'auth_handler_initialized'
            )
        
        # Setup endpoints
        self._setup_endpoints()
    
    def _setup_endpoints(self) -> None:
        """Setup endpoint methods dynamically"""
        endpoints = self.api_config.get('endpoints', {})
        
        for version, version_endpoints in endpoints.items():
            for endpoint_name, endpoint_config in version_endpoints.items():
                # Create endpoint for default version
                if version == self.default_version:
                    setattr(self, endpoint_name, APIEndpoint(self, endpoint_name, endpoint_config))
                
                # Create versioned endpoint
                versioned_name = f"{endpoint_name}_{version}"
                setattr(self, versioned_name, APIEndpoint(self, endpoint_name, endpoint_config))
    
    def _execute_endpoint(self, endpoint: APIEndpoint, **kwargs) -> Union[APIResponse, Dict[str, Any], Any]:
        """Execute an API endpoint"""
        request_id = self.logger._generate_request_id()
        start_time = time.time()
        
        try:
            # Prepare request
            request_kwargs = self._prepare_request(endpoint, **kwargs)
            
            # Log request
            self.logger.log_request(
                self.api_name, endpoint.name, endpoint.method,
                request_kwargs['url'], request_kwargs.get('headers', {}),
                request_kwargs.get('params'), request_kwargs.get('json'),
                request_id
            )
            
            # Setup retry if configured
            retry_handler = None
            if endpoint.retry_config.get('attempts', 1) > 1:
                retry_handler = RetryHandler(
                    max_attempts=endpoint.retry_config.get('attempts', 3),
                    base_delay=endpoint.retry_config.get('delay', 1.0),
                    backoff_factor=endpoint.retry_config.get('backoff_factor', 2.0),
                    jitter=endpoint.retry_config.get('jitter', True)
                )
            
            # Execute request
            if retry_handler:
                response = retry_handler.execute_with_retry(
                    self._make_request,
                    on_retry=lambda attempt, max_attempts, delay, error: self.logger.log_retry_attempt(
                        self.api_name, endpoint.name, attempt, max_attempts, delay, error
                    ),
                    **request_kwargs
                )
            else:
                response = self._make_request(**request_kwargs)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log response
            self.logger.log_response(
                self.api_name, endpoint.name, response.status_code,
                response_time, response.headers, 
                getattr(response, '_json_data', None), request_id
            )
            
            # Handle response
            return self._handle_response(response, endpoint)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.log_response(
                self.api_name, endpoint.name, 0,
                response_time, {}, None, request_id, e
            )
            raise
    
    def _prepare_request(self, endpoint: APIEndpoint, **kwargs) -> Dict[str, Any]:
        """Prepare request parameters"""
        # Extract and validate parameters
        params = kwargs.pop('params', {})
        if params:
            params = endpoint.validate_and_prepare_params(params)
        
        # Build URL
        url = self._build_url(endpoint.path, params)
        
        # Prepare request kwargs
        request_kwargs = {
            'method': endpoint.method,
            'url': url,
            'headers': kwargs.pop('headers', {}),
            'timeout': kwargs.pop('timeout', endpoint.timeout)
        }
        
        # Add query parameters (exclude path parameters)
        query_params = {k: v for k, v in params.items() 
                       if f"{{{k}}}" not in endpoint.path}
        if query_params:
            request_kwargs['params'] = query_params
        
        # Handle request body
        if endpoint.method in ['POST', 'PUT', 'PATCH']:
            body = kwargs.pop('body', kwargs.pop('json', None))
            body = endpoint.validate_and_prepare_body(body)
            
            if body is not None:
                if hasattr(body, 'to_dict'):
                    request_kwargs['json'] = body.to_dict()
                else:
                    request_kwargs['json'] = body
        
        # Apply authentication
        if endpoint.auth_required and self.auth_handler:
            request_kwargs = self.auth_handler.apply_auth(request_kwargs)
        
        return request_kwargs
    
    def _build_url(self, path: str, params: Dict[str, Any]) -> str:
        """Build URL with path parameters"""
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            if placeholder in path:
                path = path.replace(placeholder, str(value))
        
        return urljoin(self.base_url, path.lstrip('/'))
    
    def _make_request(self, **request_kwargs) -> requests.Response:
        """Make HTTP request"""
        response = self.session.request(**request_kwargs)
        
        # Store JSON data for logging
        try:
            response._json_data = response.json()
        except:
            response._json_data = None
        
        return response
    
    def _handle_response(self, response: requests.Response, endpoint: APIEndpoint) -> Union[APIResponse, Dict[str, Any], Any]:
        """Handle API response"""
        if endpoint.raise_on_error and not response.ok:
            try:
                error_data = response.json()
            except:
                error_data = response.text
            
            raise APIError(
                f"API request failed with status {response.status_code}",
                status_code=response.status_code,
                response_data=error_data
            )
        
        # Try to get JSON response
        try:
            json_data = response.json()
        except:
            json_data = response.text
        
        # If response model is specified, return APIResponse with model
        if endpoint.response_model:
            response_model_class = ModelRegistry.get_model(endpoint.response_model)
            return APIResponse(
                data=json_data,
                status_code=response.status_code,
                headers=response.headers,
                response_model=response_model_class
            )
        
        # Return raw JSON or response object
        return json_data if json_data is not None else response
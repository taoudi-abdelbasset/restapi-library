# REST API Library - Developer Documentation

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Module Documentation](#module-documentation)
4. [Data Flow](#data-flow)
5. [Design Patterns](#design-patterns)
6. [Extension Points](#extension-points)
7. [Testing Guide](#testing-guide)
8. [Performance Considerations](#performance-considerations)

## Architecture Overview

The REST API Library follows a modular architecture with clear separation of concerns. The library is built around several key principles:

- **Configuration-Driven**: All API definitions are stored in JSON configuration files
- **Factory Pattern**: Used for creating authentication handlers and cache instances
- **Plugin Architecture**: Extensible authentication and caching systems
- **Type Safety**: Strong typing with custom type definitions and model validation
- **Environment Integration**: Seamless integration with environment variables

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    RestAPILibrary (Entry Point)                 │
├─────────────────────────────────────────────────────────────────┤
│                      ConfigParser                               │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   JSON Config   │    │  Environment    │                    │
│  │     Parser      │    │    Variables    │                    │
│  └─────────────────┘    └─────────────────┘                    │
├─────────────────────────────────────────────────────────────────┤
│                       APIClient                                 │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │   Auth Factory  │    │  Cache Factory  │                     │
│  └─────────────────┘    └─────────────────┘                     │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │   APIEndpoint   │    │   RetryHandler  │                     │
│  └─────────────────┘    └─────────────────┘                     │
├─────────────────────────────────────────────────────────────────┤
│                    Support Systems                              │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │     Logger      │    │  Model Registry │                    │
│  └─────────────────┘    └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. RestAPILibrary (Main Entry Point)

**File**: `restapi_library/__init__.py`

The main interface that users interact with. It orchestrates the initialization of all components.

```python
class RestAPILibrary:
    """Main library interface"""
    
    _redis_config: Optional[Dict[str, Any]] = None
    _global_logger: Optional[APILogger] = None
    _clients: Dict[str, APIClient] = {}
```

**Key Responsibilities:**
- Initialize configuration parser
- Set up global configurations (Redis, logging)
- Create and manage API client instances
- Provide model registration interface

**Initialization Flow:**
1. Parse configuration file/dictionary
2. Load environment variables
3. Initialize global components (logger, Redis config)
4. Create API clients for each configured API
5. Expose clients as attributes

### 2. ConfigParser (Configuration Management)

**File**: `restapi_library/core/config.py`

Handles JSON configuration parsing with environment variable substitution.

```python
class ConfigParser:
    """Parse and validate API configuration with environment variable support"""
    
    def __init__(self, config_path: Optional[str] = None, 
                 config_dict: Optional[Dict] = None,
                 env_file: Optional[str] = '.env')
```

**Key Features:**
- JSON configuration file loading
- Environment variable substitution using `${VAR_NAME:default}` syntax
- Configuration validation
- Default value application
- Nested configuration merging

**Configuration Processing Pipeline:**
1. Load JSON from file or use provided dictionary
2. Parse and substitute environment variables
3. Apply default configurations
4. Validate configuration structure
5. Make configuration available to other components

### 3. APIClient (HTTP Client Core)

**File**: `restapi_library/core/client.py`

The main HTTP client that handles request execution and response processing.

```python
class APIClient:
    """Main API client class"""
    
    def __init__(self, api_name: str, config_parser: ConfigParser, 
                 logger: Optional[APILogger] = None)
```

**Key Components:**
- **Session Management**: Uses `requests.Session` for connection pooling
- **Authentication Integration**: Applies auth handlers to requests
- **Endpoint Management**: Dynamically creates endpoint methods
- **Request/Response Processing**: Handles serialization and deserialization
- **Error Handling**: Manages HTTP errors and retries

**Request Execution Flow:**
1. Validate and prepare parameters
2. Build URL with path parameter substitution
3. Apply authentication if required
4. Execute request with retry logic
5. Process response and handle errors
6. Return processed result

### 4. APIEndpoint (Endpoint Abstraction)

**File**: `restapi_library/core/endpoint.py`

Represents a single API endpoint with its configuration and behavior.

```python
class APIEndpoint:
    """Represents a single API endpoint"""
    
    def __init__(self, client: 'APIClient', endpoint_name: str, endpoint_config: Dict[str, Any])
    
    def __call__(self, **kwargs) -> Union[APIResponse, Dict[str, Any], Any]:
        """Execute the endpoint"""
```

**Endpoint Features:**
- **Parameter Validation**: Validates request parameters against configuration
- **Model Integration**: Handles request/response model conversion
- **Caching**: Implements endpoint-level caching
- **Middleware Support**: Allows custom middleware functions

## Module Documentation

### Core Module (`restapi_library/core/`)

#### types.py - Type Definitions

Defines all custom types and enums used throughout the library.

```python
class AuthType(Enum):
    BEARER = "bearer"
    BASIC = "basic"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    DYNAMIC_TOKEN = "dynamic_token"
    CUSTOM = "custom"

@dataclass
class TokenInfo:
    """Token information storage"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[float] = None
    token_type: str = "Bearer"
```

**Purpose**: Provides type safety and clear interfaces between components.

#### exceptions.py - Custom Exceptions

Defines the exception hierarchy for error handling.

```python
class RestAPIException(Exception):
    """Base exception for REST API library"""

class APIError(RestAPIException):
    """API response errors"""
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
```

**Exception Hierarchy:**
- `RestAPIException` (base)
  - `ConfigurationError` (config issues)
  - `AuthenticationError` (auth failures)
  - `ValidationError` (validation failures)
  - `APIError` (HTTP errors)
  - `RetryExhaustedError` (retry failures)
  - `CacheError` (cache issues)
  - `TokenExpiredError` (token expiry)

#### defaults.py - Default Configuration

Provides default configuration values that are merged with user configuration.

```python
DEFAULT_CONFIG = {
    "timeout": 30,
    "raise_on_error": True,
    "retry": {
        "attempts": 1,
        "delay": 1.0,
        "backoff_factor": 2.0,
        "jitter": True
    },
    # ... more defaults
}
```

### Authentication Module (`restapi_library/auth/`)

#### base.py - Base Authentication Handler

Abstract base class for all authentication handlers.

```python
class BaseAuthHandler(ABC):
    """Base authentication handler"""
    
    def __init__(self, config: Dict[str, Any], cache: Optional[BaseCache] = None):
        self.config = config
        self.cache = cache
    
    @abstractmethod
    def apply_auth(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply authentication to request"""
    
    @abstractmethod
    def refresh_token(self) -> bool:
        """Refresh authentication token if needed"""
```

**Design Pattern**: Template Method Pattern - defines the structure while allowing subclasses to implement specific behavior.

#### handlers.py - Built-in Authentication Handlers

Implements common authentication methods:

```python
class BearerAuthHandler(BaseAuthHandler):
    """Bearer token authentication"""
    
    def apply_auth(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        headers = request_kwargs.get('headers', {})
        headers['Authorization'] = f"Bearer {self.config['token']}"
        request_kwargs['headers'] = headers
        return request_kwargs

class BasicAuthHandler(BaseAuthHandler):
    """Basic authentication"""
    # Implementation details...

class APIKeyAuthHandler(BaseAuthHandler):
    """API Key authentication"""
    # Implementation details...
```

#### dynamic_token.py - Dynamic Token Authentication

Complex authentication handler for APIs that require login flows.

```python
class DynamicTokenAuthHandler(BaseAuthHandler):
    """Dynamic token authentication with automatic refresh"""
    
    def __init__(self, config: Dict[str, Any], cache: Optional[BaseCache] = None):
        # Initialize login/refresh endpoints
        # Set up token placement configuration
        # Load cached tokens
    
    def _login(self) -> bool:
        """Perform login to get new token"""
    
    def _refresh_token(self) -> bool:
        """Refresh token using refresh token"""
```

**Key Features:**
- Automatic token refresh
- Configurable token placement (header, query, body)
- Token caching with TTL
- Login endpoint configuration
- Refresh token support

#### factory.py - Authentication Factory

Creates authentication handlers based on configuration.

```python
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
```

**Design Pattern**: Factory Pattern - encapsulates object creation logic.

### Models Module (`restapi_library/models/`)

#### base.py - Base Model Class

Foundation for all request/response models.

```python
class BaseModel(ABC):
    """Base class for all request/response models"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
    
    def to_json(self) -> str:
        """Convert model to JSON string"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model instance from dictionary"""
    
    @classmethod
    def from_json(cls, json_str: str):
        """Create model instance from JSON string"""
    
    def validate(self) -> bool:
        """Validate model data - override in subclasses"""
```

**Features:**
- Bidirectional serialization (dict ↔ model ↔ JSON)
- Nested model support
- Custom validation hooks
- Dataclass integration

#### registry.py - Model Registry

Manages registered models for dynamic instantiation.

```python
class ModelRegistry:
    """Registry for request/response models"""
    
    _models: Dict[str, Type[BaseModel]] = {}
    
    @classmethod
    def register_model(cls, name: str, model_class: Type[BaseModel]) -> None:
    
    @classmethod
    def get_model(cls, name: str) -> Optional[Type[BaseModel]]:
    
    @classmethod
    def create_instance(cls, name: str, data: Any) -> Optional[BaseModel]:
```

**Purpose**: Enables dynamic model creation from configuration without hardcoded imports.

#### response.py - Response Wrapper

Wraps API responses with metadata and model integration.

```python
class APIResponse(BaseModel):
    """Wrapper for API responses"""
    
    def __init__(self, data: Any, status_code: int, headers: Dict[str, str], 
                 response_model: Optional[Type[BaseModel]] = None):
    
    @property
    def data(self) -> Union[BaseModel, Dict, Any]:
        """Get parsed data as model or raw data"""
    
    @property
    def is_success(self) -> bool:
        """Check if response is successful"""
```

### Cache Module (`restapi_library/cache/`)

#### base.py - Cache Interface

Abstract interface for all cache implementations.

```python
class BaseCache(ABC):
    """Base cache interface"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
    
    @abstractmethod
    def delete(self, key: str) -> None:
    
    @abstractmethod
    def exists(self, key: str) -> bool:
    
    @abstractmethod
    def clear(self) -> None:
```

#### memory.py - In-Memory Cache

Simple in-memory cache implementation.

```python
class MemoryCache(BaseCache):
    """In-memory cache implementation"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        # Check expiration
        # Return cached value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        # Store with expiration timestamp
```

**Implementation Details:**
- Dictionary-based storage
- TTL support with expiration checking
- Thread-safe operations
- Memory cleanup on expiration

#### redis_cache.py - Redis Cache

Redis-based cache implementation for distributed caching.

```python
class RedisCache(BaseCache):
    """Redis cache implementation"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: Optional[str] = None,
                 key_prefix: str = 'restapi:', **kwargs):
        # Initialize Redis connection
        # Test connectivity
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key"""
        return f"{self.key_prefix}{key}"
```

**Features:**
- Connection pooling
- Key prefixing for namespace isolation
- JSON serialization/deserialization
- Error handling and connection recovery
- TTL support using Redis native TTL

#### factory.py - Cache Factory

Creates cache instances based on configuration.

```python
class CacheFactory:
    """Factory for creating cache instances"""
    
    _redis_config: Optional[Dict[str, Any]] = None
    _global_cache_instances: Dict[str, BaseCache] = {}
    
    @classmethod
    def create_cache(cls, cache_config: Dict[str, Any], 
                    cache_key: Optional[str] = None) -> BaseCache:
```

**Features:**
- Global cache instance management
- Configuration merging
- Singleton pattern for shared caches

### Utils Module (`restapi_library/utils/`)

#### retry.py - Retry Handler

Implements retry logic with exponential backoff.

```python
class RetryHandler:
    """Handle retry logic with exponential backoff"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, 
                 backoff_factor: float = 2.0, jitter: bool = True):
    
    def execute_with_retry(self, func: Callable, on_retry: Optional[Callable] = None, 
                          *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        # Retry loop with exponential backoff
        # Jitter calculation
        # Callback support
```

**Algorithm:**
1. Execute function
2. If fails, calculate delay: `base_delay * (backoff_factor ^ attempt)`
3. Add jitter: `delay += random(0, delay * 0.1)`
4. Sleep for calculated delay
5. Repeat until max attempts reached

#### logging.py - Enhanced Logging

Comprehensive logging for API operations.

```python
class APILogger:
    """Enhanced logging for API operations"""
    
    def __init__(self, logger: Optional[logging.Logger] = None, 
                 log_level: int = logging.INFO,
                 log_requests: bool = True,
                 log_responses: bool = True,
                 log_sensitive_data: bool = False):
    
    def log_request(self, api_name: str, endpoint: str, method: str, 
                   url: str, headers: Dict[str, str], 
                   params: Optional[Dict] = None, 
                   body: Optional[Any] = None,
                   request_id: Optional[str] = None) -> None:
    
    def log_response(self, api_name: str, endpoint: str, 
                    status_code: int, response_time: float,
                    headers: Dict[str, str], 
                    response_data: Any = None,
                    request_id: Optional[str] = None,
                    error: Optional[Exception] = None) -> None:
```

**Features:**
- Structured JSON logging
- Request/response correlation via request ID
- Sensitive data masking
- Performance metrics (response time)
- Configurable log levels
- Auth event logging
- Retry attempt logging

#### env_parser.py - Environment Variable Parser

Handles environment variable substitution in configuration.

```python
class EnvParser:
    """Parse environment variables in configuration"""
    
    ENV_PATTERN = re.compile(r'\$\{([^}]+)\}')
    
    @classmethod
    def parse_value(cls, value: Any) -> Any:
        """Parse environment variables in a value"""
        # Support ${VAR:default} syntax
        # Recursive parsing for nested structures
    
    @classmethod
    def parse_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively parse environment variables in configuration"""
```

**Pattern Support:**
- `${VAR_NAME}` - Required variable
- `${VAR_NAME:default}` - Variable with default value
- Recursive parsing for nested dictionaries and lists

#### validation.py - Parameter Validation

Validates request parameters and models.

```python
class Validator:
    """Parameter and model validation"""
    
    @staticmethod
    def validate_type(value: Any, expected_type: str) -> bool:
        """Validate value type"""
    
    @staticmethod
    def validate_required(params: Dict[str, Any], param_config: Dict[str, Dict]) -> None:
        """Validate required parameters"""
    
    @staticmethod
    def validate_params(params: Dict[str, Any], param_config: Dict[str, Dict]) -> Dict[str, Any]:
        """Validate and process parameters"""
```

**Validation Features:**
- Type checking (int, str, float, bool, list, dict)
- Required parameter validation
- Type conversion
- Custom validation rules

## Data Flow

### Request Processing Flow

```
User Call → APIEndpoint → APIClient → Request Processing Pipeline
                                           ↓
1. Parameter Validation ← Validator ← Endpoint Config
                                           ↓
2. URL Building ← Path Parameters ← Base URL + Endpoint Path
                                           ↓
3. Authentication ← Auth Handler ← Auth Config
                                           ↓
4. Request Execution ← Retry Handler ← HTTP Session
                                           ↓
5. Response Processing ← Model Registry ← Response Model Config
                                           ↓
6. Logging ← APILogger ← Log Config
                                           ↓
7. Caching (if enabled) ← Cache Factory ← Cache Config
                                           ↓
8. Return Response ← APIResponse ← Processed Data
```

### Configuration Loading Flow

```
JSON Config File → ConfigParser → Environment Variable Substitution
                                           ↓
Default Config Merge → Validation → API Config Objects
                                           ↓
Factory Pattern Application → Component Initialization
                                           ↓
APIClient Creation → Endpoint Registration → Ready for Use
```

### Authentication Flow (Dynamic Token)

```
Request Triggered → Check Token Cache → Token Valid?
                                           ↓ No
Login Required → Execute Login Request → Extract Token Info
                                           ↓
Cache Token → Apply to Request → Continue Request
                                           ↓
Token Expired? → Refresh Token → Update Cache → Apply to Request
```

## Design Patterns

### 1. Factory Pattern

Used extensively for creating components based on configuration:

- **AuthFactory**: Creates authentication handlers
- **CacheFactory**: Creates cache instances
- **ModelRegistry**: Creates model instances

**Benefits:**
- Decouples object creation from usage
- Enables runtime configuration
- Simplifies adding new implementations

### 2. Template Method Pattern

Implemented in `BaseAuthHandler` and `BaseCache`:

```python
class BaseAuthHandler(ABC):
    def apply_auth(self, request_kwargs):
        # Template method - calls abstract methods
        return self._apply_specific_auth(request_kwargs)
    
    @abstractmethod
    def _apply_specific_auth(self, request_kwargs):
        pass
```

**Benefits:**
- Defines algorithm structure
- Allows customization of specific steps
- Promotes code reuse

### 3. Registry Pattern

Used in `ModelRegistry` for dynamic model management:

```python
class ModelRegistry:
    _models: Dict[str, Type[BaseModel]] = {}
    
    @classmethod
    def register_model(cls, name: str, model_class: Type[BaseModel]):
        cls._models[name] = model_class
```

**Benefits:**
- Runtime registration and lookup
- Decouples model definitions from usage
- Enables configuration-driven model usage

### 4. Decorator Pattern

Used for middleware and enhancements:

```python
@rate_limit(calls_per_second=10)
@cache_result(ttl=3600)
def api_call():
    # Original function
    pass
```

**Benefits:**
- Adds functionality without modifying original code
- Composable enhancements
- Clean separation of concerns

### 5. Strategy Pattern

Implemented for different authentication and caching strategies:

```python
class APIClient:
    def __init__(self, auth_handler: BaseAuthHandler):
        self.auth_handler = auth_handler
    
    def make_request(self, request_kwargs):
        # Strategy pattern - delegate to handler
        return self.auth_handler.apply_auth(request_kwargs)
```

**Benefits:**
- Runtime algorithm selection
- Easy addition of new strategies
- Encapsulates varying behavior

## Extension Points

### 1. Custom Authentication Handlers

Create new authentication methods by extending `BaseAuthHandler`:

```python
class CustomAuthHandler(BaseAuthHandler):
    def apply_auth(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        # Custom authentication logic
        return request_kwargs
    
    def refresh_token(self) -> bool:
        # Custom token refresh logic
        return True

# Register in factory
AuthFactory._handlers[AuthType.CUSTOM] = CustomAuthHandler
```

### 2. Custom Cache Implementations

Implement new cache backends by extending `BaseCache`:

```python
class DatabaseCache(BaseCache):
    def __init__(self, connection_string: str):
        # Initialize database connection
        pass
    
    def get(self, key: str) -> Optional[Any]:
        # Database-specific get implementation
        pass
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        # Database-specific set implementation
        pass
```

### 3. Custom Models

Create request/response models by extending `BaseModel`:

```python
@dataclass
class CustomModel(BaseModel):
    field1: str
    field2: int
    
    def validate(self) -> bool:
        # Custom validation logic
        return len(self.field1) > 0 and self.field2 > 0
    
    def transform_response(self, raw_data: Dict) -> Dict:
        # Custom response transformation
        return raw_data

# Register model
RestAPILibrary.register_model('CustomModel', CustomModel)
```

### 4. Custom Middleware

Add middleware to endpoints:

```python
def logging_middleware(request_kwargs, response):
    # Custom logging logic
    print(f"Request: {request_kwargs}")
    print(f"Response: {response}")
    return response

def auth_middleware(request_kwargs, response):
    # Custom auth validation
    if not validate_auth(request_kwargs):
        raise AuthenticationError("Invalid auth")
    return response

# Add to endpoint
endpoint.add_middleware(logging_middleware)
endpoint.add_middleware(auth_middleware)
```

### 5. Custom Retry Logic

Implement custom retry strategies:

```python
class CustomRetryHandler(RetryHandler):
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        # Custom retry logic based on exception type
        if isinstance(exception, ConnectionError):
            return attempt < 5
        elif isinstance(exception, TimeoutError):
            return attempt < 3
        return False
    
    def calculate_delay(self, attempt: int, exception: Exception) -> float:
        # Custom delay calculation
        if isinstance(exception, RateLimitError):
            return 60  # Wait 1 minute for rate limits
        return super().calculate_delay(attempt)
```

## Testing Guide

### Unit Testing Structure

```python
import pytest
from unittest.mock import Mock, patch
from restapi_library import RestAPILibrary, BaseModel
from restapi_library.core.exceptions import APIError

class TestRestAPILibrary:
    def setup_method(self):
        self.config = {
            "test-api": {
                "base_url": "https://api.test.com",
                "endpoints": {
                    "v1": {
                        "get_user": {
                            "path": "/users/{user_id}",
                            "method": "GET"
                        }
                    }
                }
            }
        }
    
    def test_initialization(self):
        api = RestAPILibrary(config_dict=self.config)
        assert hasattr(api, 'test_api')
    
    @patch('requests.Session.request')
    def test_api_call_success(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": 123, "name": "Test User"}
        mock_request.return_value = mock_response
        
        api = RestAPILibrary(config_dict=self.config)
        response = api.test_api.get_user(params={'user_id': 123})
        
        assert response['id'] == 123
        assert response['name'] == "Test User"
    
    @patch('requests.Session.request')
    def test_api_call_error(self, mock_request):
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        mock_request.return_value = mock_response
        
        api = RestAPILibrary(config_dict=self.config)
        
        with pytest.raises(APIError) as exc_info:
            api.test_api.get_user(params={'user_id': 999})
        
        assert exc_info.value.status_code == 404
```

### Integration Testing

```python
class TestIntegration:
    def test_auth_integration(self):
        config = {
            "api": {
                "base_url": "https://httpbin.org",
                "auth": {
                    "type": "bearer",
                    "token": "test-token"
                },
                "endpoints": {
                    "v1": {
                        "test_auth": {
                            "path": "/bearer",
                            "method": "GET",
                            "auth_required": True
                        }
                    }
                }
            }
        }
        
        api = RestAPILibrary(config_dict=config)
        response = api.api.test_auth()
        
        assert response['authenticated'] == True
        assert response['token'] == "test-token"
    
    def test_cache_integration(self):
        config = {
            "api": {
                "base_url": "https://httpbin.org",
                "cache": {"type": "memory", "ttl": 300},
                "endpoints": {
                    "v1": {
                        "get_data": {
                            "path": "/json",
                            "method": "GET",
                            "cache": {"enabled": True, "ttl": 60}
                        }
                    }
                }
            }
        }
        
        api = RestAPILibrary(config_dict=config)
        
        # First call - should hit API
        response1 = api.api.get_data()
        
        # Second call - should hit cache
        response2 = api.api.get_data()
        
        assert response1 == response2
```

### Performance Testing

```python
import time
import concurrent.futures

class TestPerformance:
    def test_concurrent_requests(self):
        config = {
            "api": {
                "base_url": "https://httpbin.org",
                "endpoints": {
                    "v1": {
                        "get_data": {
                            "path": "/json",
                            "method": "GET"
                        }
                    }
                }
            }
        }
        
        api = RestAPILibrary(config_dict=config)
        
        def make_request():
            return api.api.get_data()
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        assert len(results) == 50
        assert end_time - start_time < 30  # Should complete within 30 seconds
    
    def test_memory_usage(self):
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create multiple API instances
        for i in range(100):
            config = {
                f"api-{i}": {
                    "base_url": f"https://api{i}.example.com",
                    "endpoints": {
                        "v1": {
                            "test": {
                                "path": "/test",
                                "method": "GET"
                            }
                        }
                    }
                }
            }
            api = RestAPILibrary(config_dict=config)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024
```

## Performance Considerations

### 1. Connection Pooling

The library uses `requests.Session` for automatic connection pooling:

```python
class APIClient:
    def __init__(self, ...):
        self.session = requests.Session()
        # Connection pooling is handled automatically
```

**Benefits:**
- Reduces connection establishment overhead
- Improves performance for multiple requests
- Maintains persistent connections to reduce latency

### 2. Caching Strategy

Different caching levels provide performance optimization:

```python
# Global API-level caching
{
  "cache": {
    "type": "redis",
    "ttl": 3600
  }
}

# Endpoint-specific caching
{
  "endpoints": {
    "v1": {
      "get_data": {
        "cache": {
          "enabled": True,
          "ttl": 300  # Override global TTL
        }
      }
    }
  }
}
```

**Performance Impact:**
- Memory cache: ~0.1ms access time
- Redis cache: ~1-5ms access time (depending on network)
- API call: 50-500ms (depending on API)

### 3. Async Considerations

While the current implementation is synchronous, the architecture supports async extension:

```python
# Future async implementation example
class AsyncAPIClient:
    async def _execute_endpoint(self, endpoint: APIEndpoint, **kwargs):
        async with aiohttp.ClientSession() as session:
            response = await session.request(**request_kwargs)
            return await self._handle_response(response, endpoint)
```

### 4. Memory Management

**Token Caching:**
```python
class DynamicTokenAuthHandler:
    def __init__(self, ...):
        # Use weak references for cache to prevent memory leaks
        self._token_cache = weakref.WeakValueDictionary()
```

**Model Registry:**
```python
class ModelRegistry:
    @classmethod
    def clear_cache(cls):
        """Clear model cache to free memory"""
        cls._models.clear()
```

### 5. Request Batching

For high-volume scenarios, implement request batching:

```python
class BatchAPIClient(APIClient):
    def __init__(self, ...):
        super().__init__(...)
        self._batch_queue = []
        self._batch_size = 10
        self._batch_timeout = 1.0
    
    def batch_request(self, endpoint: APIEndpoint, **kwargs):
        """Add request to batch queue"""
        self._batch_queue.append((endpoint, kwargs))
        
        if len(self._batch_queue) >= self._batch_size:
            return self._execute_batch()
    
    def _execute_batch(self):
        """Execute batched requests"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for endpoint, kwargs in self._batch_queue:
                future = executor.submit(super()._execute_endpoint, endpoint, **kwargs)
                futures.append(future)
            
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            self._batch_queue.clear()
            return results
```

## Advanced Implementation Details

### Configuration Processing Pipeline

The configuration processing involves several stages:

```python
def _process_configuration(config_data: Dict) -> Dict:
    """
    Configuration processing pipeline:
    1. Load raw configuration
    2. Parse environment variables
    3. Apply defaults
    4. Validate structure
    5. Resolve references
    6. Create component configs
    """
    
    # Stage 1: Load raw configuration
    raw_config = json.loads(config_data) if isinstance(config_data, str) else config_data
    
    # Stage 2: Parse environment variables
    parsed_config = EnvParser.parse_config(raw_config)
    
    # Stage 3: Apply defaults
    merged_config = deep_merge(DEFAULT_CONFIG, parsed_config)
    
    # Stage 4: Validate structure
    validator = ConfigValidator()
    validator.validate(merged_config)
    
    # Stage 5: Resolve references (e.g., model references)
    resolved_config = resolve_references(merged_config)
    
    # Stage 6: Create component configs
    component_configs = create_component_configs(resolved_config)
    
    return component_configs
```

### Authentication Handler Lifecycle

Each authentication handler follows a specific lifecycle:

```python
class AuthHandlerLifecycle:
    """
    Authentication Handler Lifecycle:
    1. Initialize - Load configuration and setup
    2. Authenticate - Initial authentication if needed
    3. Apply - Apply authentication to requests
    4. Refresh - Refresh tokens when needed
    5. Cleanup - Clean up resources
    """
    
    def initialize(self, config: Dict[str, Any]):
        """Initialize handler with configuration"""
        self.config = config
        self.setup_cache()
        self.setup_endpoints()
    
    def authenticate(self) -> bool:
        """Perform initial authentication"""
        if self.requires_initial_auth():
            return self.perform_initial_auth()
        return True
    
    def apply(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply authentication to request"""
        if self.needs_refresh():
            self.refresh_token()
        return self.add_auth_headers(request_kwargs)
    
    def refresh_token(self) -> bool:
        """Refresh authentication token"""
        if self.can_refresh():
            return self.perform_refresh()
        return self.re_authenticate()
    
    def cleanup(self):
        """Clean up resources"""
        self.clear_cache()
        self.close_connections()
```

### Request Processing Pipeline

The complete request processing pipeline:

```python
def process_request(endpoint: APIEndpoint, **kwargs) -> Any:
    """
    Complete request processing pipeline:
    1. Pre-processing
    2. Parameter validation
    3. Authentication
    4. Request execution
    5. Response processing
    6. Post-processing
    """
    
    # Stage 1: Pre-processing
    request_context = create_request_context(endpoint, kwargs)
    middleware_chain = build_middleware_chain(endpoint)
    
    # Stage 2: Parameter validation
    validated_params = validate_parameters(kwargs.get('params', {}), endpoint.params_config)
    validated_body = validate_body(kwargs.get('body'), endpoint)
    
    # Stage 3: Authentication
    if endpoint.auth_required:
        request_kwargs = apply_authentication(request_kwargs, endpoint.client.auth_handler)
    
    # Stage 4: Request execution
    response = execute_request_with_retry(request_kwargs, endpoint.retry_config)
    
    # Stage 5: Response processing
    processed_response = process_response(response, endpoint)
    
    # Stage 6: Post-processing
    final_response = apply_middleware_chain(processed_response, middleware_chain)
    
    return final_response
```

### Error Handling Strategy

Comprehensive error handling across all components:

```python
class ErrorHandlingStrategy:
    """
    Error handling strategy:
    1. Categorize errors
    2. Apply retry logic
    3. Transform errors
    4. Log errors
    5. Return appropriate response
    """
    
    def handle_error(self, error: Exception, context: RequestContext) -> Any:
        """Main error handling entry point"""
        
        # Stage 1: Categorize error
        error_category = self.categorize_error(error)
        
        # Stage 2: Apply retry logic
        if self.should_retry(error_category, context):
            return self.retry_request(context)
        
        # Stage 3: Transform error
        transformed_error = self.transform_error(error, context)
        
        # Stage 4: Log error
        self.log_error(transformed_error, context)
        
        # Stage 5: Return appropriate response
        if context.endpoint.raise_on_error:
            raise transformed_error
        else:
            return self.create_error_response(transformed_error)
    
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error for handling strategy"""
        if isinstance(error, requests.ConnectionError):
            return ErrorCategory.NETWORK
        elif isinstance(error, requests.Timeout):
            return ErrorCategory.TIMEOUT
        elif isinstance(error, requests.HTTPError):
            return ErrorCategory.HTTP
        elif isinstance(error, AuthenticationError):
            return ErrorCategory.AUTH
        else:
            return ErrorCategory.UNKNOWN
    
    def should_retry(self, category: ErrorCategory, context: RequestContext) -> bool:
        """Determine if error should be retried"""
        retry_config = context.endpoint.retry_config
        
        if context.attempt_count >= retry_config.get('max_attempts', 3):
            return False
        
        if category in [ErrorCategory.NETWORK, ErrorCategory.TIMEOUT]:
            return True
        elif category == ErrorCategory.HTTP:
            status_code = getattr(context.last_error, 'response', {}).get('status_code')
            return status_code in [500, 502, 503, 504]
        elif category == ErrorCategory.AUTH:
            return context.auth_handler.can_refresh_token()
        
        return False
```

### Cache Implementation Details

Advanced caching with different strategies:

```python
class AdvancedCacheManager:
    """
    Advanced cache management with multiple strategies:
    1. L1 Cache - Memory (fastest)
    2. L2 Cache - Redis (distributed)
    3. Cache invalidation
    4. Cache warming
    5. Cache metrics
    """
    
    def __init__(self):
        self.l1_cache = MemoryCache()  # Local memory cache
        self.l2_cache = None  # Redis cache (optional)
        self.cache_metrics = CacheMetrics()
    
    def get(self, key: str) -> Optional[Any]:
        """Multi-level cache get"""
        start_time = time.time()
        
        # Try L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            self.cache_metrics.record_hit('l1', time.time() - start_time)
            return value
        
        # Try L2 cache
        if self.l2_cache:
            value = self.l2_cache.get(key)
            if value is not None:
                # Populate L1 cache
                self.l1_cache.set(key, value, ttl=300)  # 5 min L1 TTL
                self.cache_metrics.record_hit('l2', time.time() - start_time)
                return value
        
        self.cache_metrics.record_miss(time.time() - start_time)
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Multi-level cache set"""
        # Set in L1 cache
        l1_ttl = min(ttl or 3600, 300) if ttl else 300  # Max 5 min for L1
        self.l1_cache.set(key, value, l1_ttl)
        
        # Set in L2 cache
        if self.l2_cache:
            self.l2_cache.set(key, value, ttl)
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate cache entries matching pattern"""
        if self.l2_cache and hasattr(self.l2_cache, 'delete_pattern'):
            self.l2_cache.delete_pattern(pattern)
        
        # For L1, we'll need to check all keys
        self.l1_cache.invalidate_pattern(pattern)
    
    def warm_cache(self, cache_config: Dict[str, Any]) -> None:
        """Pre-populate cache with commonly accessed data"""
        warming_tasks = cache_config.get('warming', {})
        
        for task_name, task_config in warming_tasks.items():
            self.execute_warming_task(task_config)

class CacheMetrics:
    """Cache performance metrics"""
    
    def __init__(self):
        self.hits = {'l1': 0, 'l2': 0}
        self.misses = 0
        self.response_times = []
    
    def record_hit(self, level: str, response_time: float):
        self.hits[level] += 1
        self.response_times.append(response_time)
    
    def record_miss(self, response_time: float):
        self.misses += 1
        self.response_times.append(response_time)
    
    def get_hit_rate(self) -> float:
        total_hits = sum(self.hits.values())
        total_requests = total_hits + self.misses
        return total_hits / total_requests if total_requests > 0 else 0.0
    
    def get_average_response_time(self) -> float:
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
```

### Model System Deep Dive

Advanced model features and implementation:

```python
class AdvancedBaseModel(BaseModel):
    """
    Advanced model with additional features:
    1. Field validation
    2. Transformation hooks
    3. Serialization customization
    4. Relationship handling
    5. Caching
    """
    
    def __init_subclass__(cls, **kwargs):
        """Automatic model registration and validation setup"""
        super().__init_subclass__(**kwargs)
        
        # Auto-register model
        ModelRegistry.register_model(cls.__name__, cls)
        
        # Setup field validators
        cls._setup_field_validators()
        
        # Setup transformation hooks
        cls._setup_transformation_hooks()
    
    @classmethod
    def _setup_field_validators(cls):
        """Setup field-level validators"""
        cls._field_validators = {}
        
        for field_name, field_type in cls.__annotations__.items():
            validator = cls._create_field_validator(field_name, field_type)
            if validator:
                cls._field_validators[field_name] = validator
    
    def validate_field(self, field_name: str, value: Any) -> bool:
        """Validate individual field"""
        if field_name in self._field_validators:
            return self._field_validators[field_name](value)
        return True
    
    def validate(self) -> bool:
        """Enhanced validation with field-level checks"""
        # Field-level validation
        for field_name in self.__annotations__:
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if not self.validate_field(field_name, value):
                    return False
        
        # Model-level validation
        return self.validate_model()
    
    def validate_model(self) -> bool:
        """Override for custom model validation"""
        return True
    
    def transform_for_request(self) -> Dict[str, Any]:
        """Transform model for API request"""
        data = self.to_dict()
        return self.apply_request_transformations(data)
    
    def transform_from_response(self, response_data: Dict[str, Any]) -> None:
        """Transform response data into model"""
        transformed_data = self.apply_response_transformations(response_data)
        self.update_from_dict(transformed_data)
    
    @classmethod
    def from_response(cls, response_data: Dict[str, Any]):
        """Create model instance from API response"""
        instance = cls()
        instance.transform_from_response(response_data)
        return instance
    
    def apply_request_transformations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply request-specific transformations"""
        # Example: Convert snake_case to camelCase
        transformed = {}
        for key, value in data.items():
            camel_key = self.snake_to_camel(key)
            transformed[camel_key] = value
        return transformed
    
    def apply_response_transformations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply response-specific transformations"""
        # Example: Convert camelCase to snake_case
        transformed = {}
        for key, value in data.items():
            snake_key = self.camel_to_snake(key)
            transformed[snake_key] = value
        return transformed
    
    @staticmethod
    def snake_to_camel(snake_str: str) -> str:
        """Convert snake_case to camelCase"""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    @staticmethod
    def camel_to_snake(camel_str: str) -> str:
        """Convert camelCase to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class ModelRelationship:
    """Handle model relationships"""
    
    def __init__(self, model_class: Type[BaseModel], relationship_type: str = 'one'):
        self.model_class = model_class
        self.relationship_type = relationship_type  # 'one', 'many'
    
    def resolve(self, data: Any) -> Union[BaseModel, List[BaseModel]]:
        """Resolve relationship data to model instances"""
        if self.relationship_type == 'one':
            return self.model_class.from_dict(data) if data else None
        elif self.relationship_type == 'many':
            return [self.model_class.from_dict(item) for item in data] if data else []

# Example usage of advanced models
@dataclass
class UserModel(AdvancedBaseModel):
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    profile: Optional['ProfileModel'] = field(default=None, metadata={'relationship': 'one'})
    orders: List['OrderModel'] = field(default_factory=list, metadata={'relationship': 'many'})
    
    def validate_model(self) -> bool:
        """Custom model validation"""
        if not self.email or '@' not in self.email:
            return False
        if not self.name or len(self.name) < 2:
            return False
        return True
    
    def apply_request_transformations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom request transformations"""
        transformed = super().apply_request_transformations(data)
        
        # Remove None values
        transformed = {k: v for k, v in transformed.items() if v is not None}
        
        # Format email to lowercase
        if 'email' in transformed:
            transformed['email'] = transformed['email'].lower()
        
        return transformed
```

### Monitoring and Observability

Built-in monitoring and observability features:

```python
class APIMonitor:
    """
    Comprehensive API monitoring:
    1. Request/response metrics
    2. Performance tracking
    3. Error rate monitoring
    4. Health checks
    5. Custom metrics
    """
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_error': 0,
            'response_times': [],
            'error_rates': {},
            'endpoint_metrics': {}
        }
        self.health_checks = {}
    
    def record_request(self, api_name: str, endpoint: str, method: str):
        """Record request start"""
        self.metrics['requests_total'] += 1
        
        endpoint_key = f"{api_name}.{endpoint}.{method}"
        if endpoint_key not in self.metrics['endpoint_metrics']:
            self.metrics['endpoint_metrics'][endpoint_key] = {
                'count': 0,
                'success': 0,
                'error': 0,
                'response_times': []
            }
        
        self.metrics['endpoint_metrics'][endpoint_key]['count'] += 1
    
    def record_response(self, api_name: str, endpoint: str, method: str, 
                       response_time: float, status_code: int, error: Optional[Exception] = None):
        """Record response completion"""
        endpoint_key = f"{api_name}.{endpoint}.{method}"
        endpoint_metrics = self.metrics['endpoint_metrics'][endpoint_key]
        
        # Record response time
        self.metrics['response_times'].append(response_time)
        endpoint_metrics['response_times'].append(response_time)
        
        # Record success/error
        if error or status_code >= 400:
            self.metrics['requests_error'] += 1
            endpoint_metrics['error'] += 1
            
            # Track error types
            error_type = type(error).__name__ if error else f"HTTP_{status_code}"
            if error_type not in self.metrics['error_rates']:
                self.metrics['error_rates'][error_type] = 0
            self.metrics['error_rates'][error_type] += 1
        else:
            self.metrics['requests_success'] += 1
            endpoint_metrics['success'] += 1
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        total_requests = self.metrics['requests_total']
        if total_requests == 0:
            return {'status': 'unknown', 'details': 'No requests recorded'}
        
        success_rate = self.metrics['requests_success'] / total_requests
        avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        
        status = 'healthy'
        if success_rate < 0.95:  # Less than 95% success rate
            status = 'degraded'
        if success_rate < 0.90:  # Less than 90% success rate
            status = 'unhealthy'
        if avg_response_time > 5000:  # More than 5 seconds average
            status = 'unhealthy'
        
        return {
            'status': status,
            'success_rate': success_rate,
            'average_response_time': avg_response_time,
            'total_requests': total_requests,
            'error_distribution': self.metrics['error_rates']
        }
    
    def add_health_check(self, name: str, check_function: Callable[[], bool]):
        """Add custom health check"""
        self.health_checks[name] = check_function
    
    def run_health_checks(self) -> Dict[str, bool]:
        """Run all health checks"""
        results = {}
        for name, check_function in self.health_checks.items():
            try:
                results[name] = check_function()
            except Exception:
                results[name] = False
        return results

class PerformanceProfiler:
    """Performance profiling for API operations"""
    
    def __init__(self):
        self.profiles = {}
    
    def profile_request(self, api_name: str, endpoint: str):
        """Context manager for profiling requests"""
        return RequestProfiler(self, api_name, endpoint)
    
    def record_profile(self, key: str, profile_data: Dict[str, Any]):
        """Record profiling data"""
        if key not in self.profiles:
            self.profiles[key] = []
        self.profiles[key].append(profile_data)
    
    def get_performance_summary(self, key: str) -> Dict[str, Any]:
        """Get performance summary for a specific operation"""
        if key not in self.profiles:
            return {}
        
        profiles = self.profiles[key]
        
        response_times = [p['response_time'] for p in profiles]
        auth_times = [p.get('auth_time', 0) for p in profiles]
        cache_times = [p.get('cache_time', 0) for p in profiles]
        
        return {
            'count': len(profiles),
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'avg_auth_time': sum(auth_times) / len(auth_times),
            'avg_cache_time': sum(cache_times) / len(cache_times),
            'percentiles': {
                'p50': self._percentile(response_times, 50),
                'p95': self._percentile(response_times, 95),
                'p99': self._percentile(response_times, 99)
            }
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(percentile / 100 * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]

class RequestProfiler:
    """Context manager for profiling individual requests"""
    
    def __init__(self, profiler: PerformanceProfiler, api_name: str, endpoint: str):
        self.profiler = profiler
        self.key = f"{api_name}.{endpoint}"
        self.profile_data = {}
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profile_data['response_time'] = (time.time() - self.start_time) * 1000  # ms
        self.profiler.record_profile(self.key, self.profile_data)
    
    def record_auth_time(self, auth_time: float):
        """Record authentication time"""
        self.profile_data['auth_time'] = auth_time * 1000  # ms
    
    def record_cache_time(self, cache_time: float):
        """Record cache operation time"""
        self.profile_data['cache_time'] = cache_time * 1000  # ms
```

### Security Implementation

Security features and best practices:

```python
class SecurityManager:
    """
    Security management for API operations:
    1. Input sanitization
    2. Output filtering
    3. Secret management
    4. Request signing
    5. Rate limiting
    """
    
    def __init__(self):
        self.secret_patterns = [
            r'(?i)(password|passwd|pwd|secret|key|token|auth)',
            r'(?i)(api_key|apikey|access_key|secret_key)',
            r'(?i)(bearer|basic|oauth)',
            r'[a-zA-Z0-9]{32,}',  # Potential API keys
        ]
        self.rate_limiters = {}
    
    def sanitize_input(self, data: Any) -> Any:
        """Sanitize input data"""
        if isinstance(data, dict):
            return {key: self.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        elif isinstance(data, str):
            return self.sanitize_string(data)
        else:
            return data
    
    def sanitize_string(self, text: str) -> str:
        """Sanitize string input"""
        # Remove potential XSS patterns
        import html
        text = html.escape(text)
        
        # Remove SQL injection patterns
        dangerous_patterns = [
            r"('|(\\'))+.*(--)|(\\0)",
            r"((\w+)((\s)+)?(=)(\s)*((\w+)((\s)+)?(\w+))*(;|'))|(((')|(\-\-)|(\w+))",
            r"union.*select",
            r"insert.*into",
            r"delete.*from",
            r"update.*set",
            r"drop.*table"
        ]
        
        import re
        for pattern in dangerous_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
        return text
    
    def filter_sensitive_data(self, data: Any) -> Any:
        """Filter sensitive data from logs/responses"""
        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                if self.is_sensitive_field(key):
                    filtered[key] = '[REDACTED]'
                else:
                    filtered[key] = self.filter_sensitive_data(value)
            return filtered
        elif isinstance(data, list):
            return [self.filter_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            return self.filter_sensitive_string(data)
        else:
            return data
    
    def is_sensitive_field(self, field_name: str) -> bool:
        """Check if field contains sensitive data"""
        import re
        for pattern in self.secret_patterns:
            if re.search(pattern, field_name):
                return True
        return False
    
    def filter_sensitive_string(self, text: str) -> str:
        """Filter sensitive patterns from strings"""
        import re
        
        # Mask potential secrets
        for pattern in self.secret_patterns:
            text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)
        
        return text
    
    def sign_request(self, request_data: Dict[str, Any], secret_key: str) -> str:
        """Sign request for integrity verification"""
        import hmac
        import hashlib
        import json
        
        # Create canonical request string
        canonical_string = json.dumps(request_data, sort_keys=True, separators=(',', ':'))
        
        # Generate signature
        signature = hmac.new(
            secret_key.encode('utf-8'),
            canonical_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, request_data: Dict[str, Any], signature: str, secret_key: str) -> bool:
        """Verify request signature"""
        expected_signature = self.sign_request(request_data, secret_key)
        return hmac.compare_digest(signature, expected_signature)
    
    def apply_rate_limit(self, identifier: str, limit: int, window: int) -> bool:
        """Apply rate limiting"""
        current_time = time.time()
        
        if identifier not in self.rate_limiters:
            self.rate_limiters[identifier] = []
        
        # Clean old entries
        self.rate_limiters[identifier] = [
            timestamp for timestamp in self.rate_limiters[identifier]
            if current_time - timestamp < window
        ]
        
        # Check limit
        if len(self.rate_limiters[identifier]) >= limit:
            return False
        
        # Add current request
        self.rate_limiters[identifier].append(current_time)
        return True

class SecureConfigManager:
    """Secure configuration management"""
    
    def __init__(self):
        self.encryption_key = self.generate_encryption_key()
    
    def generate_encryption_key(self) -> bytes:
        """Generate encryption key for sensitive data"""
        from cryptography.fernet import Fernet
        return Fernet.generate_key()
    
    def encrypt_sensitive_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive configuration values"""
        from cryptography.fernet import Fernet
        
        fernet = Fernet(self.encryption_key)
        encrypted_config = {}
        
        for key, value in config.items():
            if self.is_sensitive_config_key(key):
                if isinstance(value, str):
                    encrypted_value = fernet.encrypt(value.encode()).decode()
                    encrypted_config[key] = f"encrypted:{encrypted_value}"
                else:
                    encrypted_config[key] = value
            elif isinstance(value, dict):
                encrypted_config[key] = self.encrypt_sensitive_config(value)
            else:
                encrypted_config[key] = value
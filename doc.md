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
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   Auth Factory  │    │  Cache Factory  │                    │
│  └─────────────────┘    └─────────────────┘                    │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   APIEndpoint   │    │   RetryHandler  │                    │
│  └─────────────────┘    └─────────────────┘                    │
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

### 3. Memory Management

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


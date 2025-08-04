# REST API Library

A comprehensive Python library for managing REST API clients with advanced features including authentication, caching, retry logic, request/response models, and environment variable support.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [Caching](#caching)
- [Models](#models)
- [Advanced Features](#advanced-features)
- [API Reference](#api-reference)
- [Examples](#examples)
- [CLI Tools](#cli-tools)
- [Contributing](#contributing)

## Features

- 🚀 **Easy Configuration**: JSON-based configuration with environment variable support
- 🔐 **Multiple Auth Types**: Bearer, Basic, API Key, JWT, OAuth2, and Dynamic Token authentication
- 💾 **Smart Caching**: In-memory and Redis caching with TTL support
- 🔄 **Retry Logic**: Configurable retry with exponential backoff and jitter
- 📊 **Request/Response Models**: Type-safe models with validation
- 🌍 **Environment Variables**: Secure configuration with .env file support
- 📝 **Comprehensive Logging**: Detailed request/response logging with sensitive data masking
- 🎯 **Multiple API Versions**: Support for different API versions
- ⚡ **High Performance**: Optimized for speed and reliability
- 🛠️ **CLI Tools**: Command-line tools for validation and template generation

## Installation

### Basic Installation

```bash
pip install restapi-library
```

### With Redis Support

```bash
pip install restapi-library[redis]
```

### Development Installation

```bash
pip install restapi-library[dev]
```

## Quick Start

### 1. Create Configuration File

Create a `config.json` file:

```json
{
  "api-payment": {
    "base_url": "${API_BASE_URL:https://api.payment.com}",
    "default_version": "v1",
    "auth": {
      "type": "bearer",
      "token": "${API_TOKEN}"
    },
    "endpoints": {
      "v1": {
        "get_user": {
          "path": "/users/{user_id}",
          "method": "GET",
          "params": {
            "user_id": {
              "type": "int",
              "required": true
            }
          },
          "auth_required": true
        }
      }
    }
  }
}
```

### 2. Create Environment File

Create a `.env` file:

```env
API_BASE_URL=https://api.payment.com
API_TOKEN=your_secret_token_here
```

### 3. Use the Library

```python
from restapi_library import RestAPILibrary

# Initialize the library
api = RestAPILibrary(config_path="config.json")

# Make API calls
response = api.api_payment.get_user(params={'user_id': 123})
print(response)
```

## Configuration

### Basic Structure

```json
{
  "api-name": {
    "base_url": "https://api.example.com",
    "default_version": "v1",
    "timeout": 30,
    "raise_on_error": true,
    "auth": { ... },
    "cache": { ... },
    "logging": { ... },
    "retry": { ... },
    "endpoints": { ... }
  }
}
```

### Environment Variables

Use `${VARIABLE_NAME}` syntax for environment variables:

```json
{
  "api-name": {
    "base_url": "${API_BASE_URL:https://api.default.com}",
    "auth": {
      "type": "bearer",
      "token": "${API_TOKEN}"
    }
  }
}
```

Format: `${VARIABLE_NAME:default_value}`

### Global Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `base_url` | string | Required | Base URL for the API |
| `default_version` | string | "v1" | Default API version |
| `timeout` | int | 30 | Request timeout in seconds |
| `raise_on_error` | bool | true | Raise exception on HTTP errors |

### Retry Configuration

```json
{
  "retry": {
    "attempts": 3,
    "delay": 1.0,
    "backoff_factor": 2.0,
    "jitter": true
  }
}
```

### Logging Configuration

```json
{
  "logging": {
    "enabled": true,
    "level": "INFO",
    "log_requests": true,
    "log_responses": true,
    "log_sensitive_data": false
  }
}
```

## Authentication

### Bearer Token

```json
{
  "auth": {
    "type": "bearer",
    "token": "${API_TOKEN}"
  }
}
```

### Basic Authentication

```json
{
  "auth": {
    "type": "basic",
    "username": "${API_USERNAME}",
    "password": "${API_PASSWORD}"
  }
}
```

### API Key Authentication

```json
{
  "auth": {
    "type": "api_key",
    "api_key": "${API_KEY}",
    "key_name": "X-API-Key",
    "location": "header"
  }
}
```

### Dynamic Token Authentication

For APIs that require login to get access tokens:

```json
{
  "auth": {
    "type": "dynamic_token",
    "login_endpoint": {
      "path": "/auth/login",
      "method": "POST",
      "body": {
        "username": "${API_USERNAME}",
        "password": "${API_PASSWORD}"
      },
      "token_field": "access_token",
      "refresh_token_field": "refresh_token",
      "expires_in_field": "expires_in"
    },
    "token_placement": {
      "type": "header",
      "header_name": "Authorization",
      "prefix": "Bearer"
    },
    "refresh_endpoint": {
      "path": "/auth/refresh",
      "method": "POST",
      "body_field": "refresh_token"
    },
    "cache": {
      "type": "redis",
      "ttl": 3600
    }
  }
}
```

## Caching

### In-Memory Cache

```json
{
  "cache": {
    "type": "memory",
    "ttl": 3600
  }
}
```

### Redis Cache

First, set Redis configuration:

```python
RestAPILibrary.set_redis_config({
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": "your_password"
})
```

Then use in configuration:

```json
{
  "cache": {
    "type": "redis",
    "ttl": 3600
  }
}
```

### Endpoint-Level Caching

```json
{
  "endpoints": {
    "v1": {
      "get_data": {
        "path": "/data",
        "method": "GET",
        "cache": {
          "enabled": true,
          "ttl": 300
        }
      }
    }
  }
}
```

## Models

### Defining Models

```python
from restapi_library import BaseModel
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserModel(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    
    def validate(self) -> bool:
        return "@" in self.email and len(self.name) > 0

# Register the model
RestAPILibrary.register_model('UserModel', UserModel)
```

### Using Models in Configuration

```json
{
  "endpoints": {
    "v1": {
      "create_user": {
        "path": "/users",
        "method": "POST",
        "request_model": "UserModel",
        "response_model": "UserModel",
        "body_required": true
      }
    }
  }
}
```

### Using Models in Code

```python
# Create model instance
user = UserModel(name="John Doe", email="john@example.com", age=30)

# Make API call with model
response = api.my_api.create_user(body=user)

# Response is automatically parsed to model if response_model is configured
print(response.data.name)  # Access model properties
```

## Advanced Features

### Multiple API Versions

```json
{
  "endpoints": {
    "v1": {
      "get_user": {
        "path": "/users/{user_id}",
        "method": "GET"
      }
    },
    "v2": {
      "get_user": {
        "path": "/v2/users/{user_id}",
        "method": "GET",
        "response_model": "UserV2Model"
      }
    }
  }
}
```

Usage:

```python
# Use default version (v1)
user_v1 = api.my_api.get_user(params={'user_id': 123})

# Use specific version
user_v2 = api.my_api.get_user_v2(params={'user_id': 123})
```

### Parameter Validation

```json
{
  "endpoints": {
    "v1": {
      "get_user": {
        "path": "/users/{user_id}",
        "method": "GET",
        "params": {
          "user_id": {
            "type": "int",
            "required": true
          },
          "include_profile": {
            "type": "bool",
            "required": false
          }
        }
      }
    }
  }
}
```

### Custom Headers and Timeouts

```python
# Custom headers
response = api.my_api.get_user(
    params={'user_id': 123},
    headers={'X-Custom-Header': 'value'}
)

# Custom timeout
response = api.my_api.get_user(
    params={'user_id': 123},
    timeout=60
)
```

### Error Handling

```python
from restapi_library import APIError, AuthenticationError

try:
    response = api.my_api.get_user(params={'user_id': 123})
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e}")
    print(f"Response data: {e.response_data}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## API Reference

### RestAPILibrary Class

#### Constructor

```python
RestAPILibrary(
    config_path: Optional[str] = None,
    config_dict: Optional[Dict] = None,
    env_file: Optional[str] = '.env',
    logger: Optional[APILogger] = None
)
```

#### Class Methods

```python
# Set global Redis configuration
RestAPILibrary.set_redis_config(redis_config: Dict[str, Any])

# Register model for request/response handling
RestAPILibrary.register_model(name: str, model_class: type)
```

#### Instance Methods

```python
# Get API client by name
get_client(api_name: str) -> APIClient

# List all available API names
list_apis() -> List[str]

# Reload configuration
reload_config(config_path: Optional[str] = None, config_dict: Optional[Dict] = None)
```

### BaseModel Class

#### Methods

```python
# Convert model to dictionary
to_dict() -> Dict[str, Any]

# Convert model to JSON string
to_json() -> str

# Create model from dictionary
@classmethod
from_dict(cls, data: Dict[str, Any]) -> BaseModel

# Create model from JSON string
@classmethod
from_json(cls, json_str: str) -> BaseModel

# Validate model data (override in subclasses)
validate() -> bool
```

### APIResponse Class

#### Properties

```python
# Parsed data (as model or raw data)
data: Union[BaseModel, Dict, Any]

# HTTP status code
status_code: int

# Response headers
headers: Dict[str, str]

# Check if response is successful (2xx status)
is_success: bool

# Raw response data
raw_data: Any
```

## Examples

### Complete Example with All Features

```python
from restapi_library import RestAPILibrary, BaseModel
from dataclasses import dataclass
from typing import Optional, List

# Define models
@dataclass
class UserModel(BaseModel):
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    age: Optional[int] = None
    
    def validate(self) -> bool:
        return "@" in self.email and len(self.name) > 0

@dataclass
class ProductModel(BaseModel):
    id: Optional[int] = None
    name: str = ""
    price: float = 0.0
    category: str = ""
    
    def validate(self) -> bool:
        return self.price > 0 and len(self.name) > 0

def main():
    # Set up Redis (optional)
    RestAPILibrary.set_redis_config({
        "host": "localhost",
        "port": 6379,
        "db": 0
    })
    
    # Register models
    RestAPILibrary.register_model('UserModel', UserModel)
    RestAPILibrary.register_model('ProductModel', ProductModel)
    
    # Initialize library
    api = RestAPILibrary(config_path="config.json")
    
    try:
        # Example 1: Simple GET request
        print("=== GET User ===")
        user_response = api.ecommerce_api.get_user(params={'user_id': 123})
        print(f"User: {user_response.data.name} ({user_response.data.email})")
        
        # Example 2: POST request with model
        print("\n=== CREATE User ===")
        new_user = UserModel(
            name="Jane Smith", 
            email="jane@example.com", 
            age=25
        )
        create_response = api.ecommerce_api.create_user(body=new_user)
        print(f"Created user ID: {create_response.data.id}")
        
        # Example 3: GET with query parameters
        print("\n=== GET Products ===")
        products_response = api.ecommerce_api.get_products(
            params={
                'category': 'electronics',
                'min_price': 100,
                'max_price': 1000,
                'page': 1,
                'limit': 10
            }
        )
        print(f"Found {len(products_response.data)} products")
        
        # Example 4: Different API version
        print("\n=== GET User (v2) ===")
        user_v2_response = api.ecommerce_api.get_user_v2(params={'user_id': 123})
        print(f"User v2: {user_v2_response}")
        
        # Example 5: Custom headers and timeout
        print("\n=== Custom Request ===")
        custom_response = api.ecommerce_api.get_user(
            params={'user_id': 123},
            headers={
                'X-Client-Version': '1.0',
                'X-Request-ID': 'req-12345'
            },
            timeout=60
        )
        print(f"Custom request successful: {custom_response.is_success}")
        
        # Example 6: Error handling
        print("\n=== Error Handling ===")
        try:
            error_response = api.ecommerce_api.get_user(params={'user_id': -1})
        except Exception as e:
            print(f"Expected error: {type(e).__name__}: {e}")
        
        # Example 7: List all available APIs
        print(f"\n=== Available APIs ===")
        apis = api.list_apis()
        print(f"Available APIs: {apis}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

### Configuration File for the Example

```json
{
  "ecommerce-api": {
    "base_url": "${ECOMMERCE_API_URL:https://api.ecommerce.com}",
    "default_version": "v1",
    "timeout": 30,
    "auth": {
      "type": "dynamic_token",
      "login_endpoint": {
        "path": "/auth/login",
        "method": "POST",
        "body": {
          "username": "${ECOMMERCE_USERNAME}",
          "password": "${ECOMMERCE_PASSWORD}"
        },
        "token_field": "access_token",
        "refresh_token_field": "refresh_token",
        "expires_in_field": "expires_in"
      },
      "token_placement": {
        "type": "header",
        "header_name": "Authorization",
        "prefix": "Bearer"
      },
      "refresh_endpoint": {
        "path": "/auth/refresh",
        "method": "POST",
        "body_field": "refresh_token"
      },
      "cache": {
        "type": "redis",
        "ttl": 3600
      }
    },
    "cache": {
      "type": "redis",
      "ttl": 300
    },
    "logging": {
      "enabled": true,
      "level": "INFO",
      "log_requests": true,
      "log_responses": true,
      "log_sensitive_data": false
    },
    "retry": {
      "attempts": 3,
      "delay": 1.0,
      "backoff_factor": 2.0,
      "jitter": true
    },
    "endpoints": {
      "v1": {
        "get_user": {
          "path": "/users/{user_id}",
          "method": "GET",
          "params": {
            "user_id": {
              "type": "int",
              "required": true
            }
          },
          "response_model": "UserModel",
          "auth_required": true,
          "cache": {
            "enabled": true,
            "ttl": 300
          },
          "retry": {
            "attempts": 3,
            "delay": 1.0
          }
        },
        "create_user": {
          "path": "/users",
          "method": "POST",
          "request_model": "UserModel",
          "response_model": "UserModel",
          "body_required": true,
          "auth_required": true,
          "raise_on_error": true
        },
        "get_products": {
          "path": "/products",
          "method": "GET",
          "params": {
            "category": {
              "type": "str",
              "required": false
            },
            "min_price": {
              "type": "float",
              "required": false
            },
            "max_price": {
              "type": "float",
              "required": false
            },
            "page": {
              "type": "int",
              "required": false
            },
            "limit": {
              "type": "int",
              "required": false
            }
          },
          "auth_required": true,
          "cache": {
            "enabled": true,
            "ttl": 600
          }
        }
      },
      "v2": {
        "get_user": {
          "path": "/v2/users/{user_id}",
          "method": "GET",
          "params": {
            "user_id": {
              "type": "int",
              "required": true
            }
          },
          "auth_required": true
        }
      }
    }
  }
}
```

### Environment File (.env)

```env
# API Configuration
ECOMMERCE_API_URL=https://api.ecommerce.com
ECOMMERCE_USERNAME=your_username
ECOMMERCE_PASSWORD=your_secure_password

# Redis Configuration (if using Redis cache)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Other API configurations
PAYMENT_API_URL=https://api.payment.com
PAYMENT_API_KEY=your_payment_api_key
```

## CLI Tools

The library includes command-line tools for configuration management.

### Validate Configuration

```bash
restapi-cli validate config.json
```

Output:
```
✓ Configuration file 'config.json' is valid

API: ecommerce-api
  Base URL: https://api.ecommerce.com
  Default Version: v1
  Auth Type: dynamic_token
  Endpoints: 3
```

### Generate Configuration Template

```bash
restapi-cli template -o my_config.json
```

This generates a template configuration file with all available options.

## Error Handling

### Exception Types

| Exception | Description |
|-----------|-------------|
| `RestAPIException` | Base exception for all library errors |
| `ConfigurationError` | Configuration file or setup errors |
| `AuthenticationError` | Authentication-related errors |
| `ValidationError` | Request/response validation errors |
| `APIError` | HTTP response errors (4xx, 5xx) |
| `RetryExhaustedError` | All retry attempts failed |
| `CacheError` | Cache-related errors |
| `TokenExpiredError` | Authentication token expired |

### Error Handling Best Practices

```python
from restapi_library import (
    RestAPILibrary, APIError, AuthenticationError, 
    ValidationError, ConfigurationError
)

try:
    api = RestAPILibrary(config_path="config.json")
    response = api.my_api.get_data(params={'id': 123})
    
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Handle configuration issues
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Handle auth issues, maybe refresh token
    
except ValidationError as e:
    print(f"Validation error: {e}")
    # Handle parameter or model validation errors
    
except APIError as e:
    print(f"API error {e.status_code}: {e}")
    if e.status_code == 429:
        # Handle rate limiting
        pass
    elif e.status_code >= 500:
        # Handle server errors
        pass
        
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle other errors
```

## Performance Tips

### 1. Use Caching Wisely

```json
{
  "cache": {
    "type": "redis",
    "ttl": 300
  }
}
```

Cache GET requests that don't change frequently.

### 2. Configure Timeouts

```json
{
  "timeout": 30,
  "endpoints": {
    "v1": {
      "slow_endpoint": {
        "timeout": 120
      }
    }
  }
}
```

Set appropriate timeouts for different endpoints.

### 3. Use Connection Pooling

The library uses `requests.Session` internally for connection pooling.

### 4. Optimize Retry Settings

```json
{
  "retry": {
    "attempts": 3,
    "delay": 1.0,
    "backoff_factor": 2.0,
    "jitter": true
  }
}
```

Don't over-retry for endpoints that are unlikely to succeed on retry.

## Security Best Practices

### 1. Use Environment Variables

Never hardcode sensitive information in configuration files:

```json
{
  "auth": {
    "type": "bearer",
    "token": "${API_TOKEN}"
  }
}
```

### 2. Enable Sensitive Data Masking

```json
{
  "logging": {
    "log_sensitive_data": false
  }
}
```

### 3. Use HTTPS

Always use HTTPS URLs in production:

```json
{
  "base_url": "https://api.example.com"
}
```

### 4. Secure Redis Connection

If using Redis caching:

```python
RestAPILibrary.set_redis_config({
    "host": "your-redis-host",
    "port": 6379,
    "password": "your-secure-password",
    "ssl": True,
    "ssl_cert_reqs": "required"
})
```

## Troubleshooting

### Common Issues

#### 1. Configuration File Not Found

```
ConfigurationError: Configuration file not found: config.json
```

**Solution**: Ensure the configuration file path is correct and the file exists.

#### 2. Environment Variable Not Set

```
KeyError: 'API_TOKEN'
```

**Solution**: Check your `.env` file and ensure all required environment variables are set.

#### 3. Redis Connection Failed

```
CacheError: Failed to connect to Redis: [Errno 111] Connection refused
```

**Solution**: 
- Ensure Redis server is running
- Check Redis connection parameters
- Verify network connectivity

#### 4. Authentication Failed

```
AuthenticationError: Login failed with status 401
```

**Solution**:
- Verify authentication credentials
- Check if API endpoints are correct
- Ensure token format is correct

#### 5. Model Validation Failed

```
ValidationError: Body validation failed for model 'UserModel'
```

**Solution**:
- Check model validation logic
- Ensure required fields are provided
- Verify data types match model definition

### Debug Mode

Enable detailed logging for debugging:

```json
{
  "logging": {
    "enabled": true,
    "level": "DEBUG",
    "log_requests": true,
    "log_responses": true,
    "log_sensitive_data": true
  }
}
```

**Note**: Only enable `log_sensitive_data` in development environments.

## Contributing

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/restapi-library.git
cd restapi-library
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .[dev]
```

4. Run tests:
```bash
pytest
```

5. Run linting:
```bash
flake8 restapi_library
black restapi_library
mypy restapi_library
```

### Project Structure

```
restapi_library/
├── __init__.py              # Main library interface
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── client.py           # Main API client
│   ├── config.py           # Configuration parser
│   ├── endpoint.py         # Endpoint class
│   ├── exceptions.py       # Custom exceptions
│   ├── types.py           # Type definitions
│   └── defaults.py        # Default configurations
├── auth/                   # Authentication handlers
│   ├── __init__.py
│   ├── base.py            # Base auth handler
│   ├── handlers.py        # Built-in auth handlers
│   ├── dynamic_token.py   # Dynamic token auth
│   └── factory.py         # Auth factory
├── models/                 # Request/response models
│   ├── __init__.py
│   ├── base.py            # Base model class
│   ├── registry.py        # Model registry
│   └── response.py        # Response wrapper
├── cache/                  # Caching implementations
│   ├── __init__.py
│   ├── base.py            # Base cache interface
│   ├── memory.py          # In-memory cache
│   ├── redis_cache.py     # Redis cache
│   └── factory.py         # Cache factory
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── retry.py           # Retry logic
│   ├── logging.py         # Logging utilities
│   ├── env_parser.py      # Environment parser
│   ├── validation.py      # Validation utilities
│   ├── helpers.py         # Helper functions
│   └── decorators.py      # Custom decorators
├── cli.py                  # Command-line interface
└── examples/               # Example usage
    ├── config.json
    ├── .env
    └── usage.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0
- Initial release
- Basic REST API client functionality
- Multiple authentication methods
- Caching support (memory and Redis)
- Request/response models
- Environment variable support
- Retry logic with exponential backoff
- Comprehensive logging
- CLI tools

## Support

For support, please:

1. Check the [documentation](#table-of-contents)
2. Look at [examples](#examples)
3. Check [troubleshooting](#troubleshooting)
4. Open an issue on [GitHub](https://github.com/yourusername/restapi-library/issues)

## Roadmap

- [ ] GraphQL support
- [ ] Async/await support
- [ ] Webhook handling
- [ ] OpenAPI/Swagger integration
- [ ] Rate limiting
- [ ] Circuit breaker pattern
- [ ] Metrics and monitoring
- [ ] Plugin system
- [ ] Mock server for testing
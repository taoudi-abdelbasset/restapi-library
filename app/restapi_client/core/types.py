from typing import Dict, Any, Optional, Union, List, Callable, TypeVar, Generic
from enum import Enum
from dataclasses import dataclass

# Type of enums
class AuthType(Enum):
    BEARER = "bearer"
    BASIC = "basic"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    DYNAMIC_TOKEN = "dynamic_token"
    CUSTOM = "custom"

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

    # Existent methods, but migth not use them ever
    # HEAD = "HEAD"
    # OPTIONS = "OPTIONS"

class CacheType(Enum):
    MEMORY = "memory"
    REDIS = "redis"

class TokenPlacementType(Enum):
    HEADER = "header"
    QUERY = "query"
    BODY = "body"

@dataclass
class TokenInfo:
    """Token information storage"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[float] = None
    # default token type is Bearer
    token_type: str = "Bearer"

ConfigDict = Dict[str, Any]
HeadersDict = Dict[str, str]
ParamsDict = Dict[str, Any]

T = TypeVar('T')
ModelType = TypeVar('ModelType')
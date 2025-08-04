class RestAPIException(Exception):
    """Base exception for REST API library"""
    pass

class ConfigurationError(RestAPIException):
    """Configuration related errors"""
    pass

class AuthenticationError(RestAPIException):
    """Authentication related errors"""
    pass

class ValidationError(RestAPIException):
    """Request/Response validation errors"""
    pass

class APIError(RestAPIException):
    """API response errors"""
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class RetryExhaustedError(RestAPIException):
    """Retry attempts exhausted"""
    pass

class CacheError(RestAPIException):
    """Cache related errors"""
    pass

class TokenExpiredError(AuthenticationError):
    """Token expired error"""
    pass

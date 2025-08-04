import logging
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime

class APILogger:
    """Enhanced logging for API operations"""
    
    def __init__(self, logger: Optional[logging.Logger] = None, 
                 log_level: int = logging.INFO,
                 log_requests: bool = True,
                 log_responses: bool = True,
                 log_sensitive_data: bool = False):
        
        self.logger = logger or logging.getLogger('restapi_library')
        self.log_level = log_level
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.log_sensitive_data = log_sensitive_data
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(log_level)
    
    def log_request(self, api_name: str, endpoint: str, method: str, 
                   url: str, headers: Dict[str, str], 
                   params: Optional[Dict] = None, 
                   body: Optional[Any] = None,
                   request_id: Optional[str] = None) -> None:
        """Log API request details"""
        if not self.log_requests:
            return
        
        log_data = {
            'type': 'REQUEST',
            'api_name': api_name,
            'endpoint': endpoint,
            'method': method,
            'url': url,
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': request_id or self._generate_request_id()
        }
        
        if headers:
            filtered_headers = self._filter_sensitive_data(headers) if not self.log_sensitive_data else headers
            log_data['headers'] = filtered_headers
        
        if params:
            log_data['params'] = params
        
        if body:
            if hasattr(body, 'to_dict'):
                log_data['body'] = body.to_dict()
            else:
                log_data['body'] = body
        
        self.logger.log(self.log_level, json.dumps(log_data, indent=2))
    
    def log_response(self, api_name: str, endpoint: str, 
                    status_code: int, response_time: float,
                    headers: Dict[str, str], 
                    response_data: Any = None,
                    request_id: Optional[str] = None,
                    error: Optional[Exception] = None) -> None:
        """Log API response details"""
        if not self.log_responses:
            return
        
        log_data = {
            'type': 'RESPONSE',
            'api_name': api_name,
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time_ms': round(response_time * 1000, 2),
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': request_id,
            'success': 200 <= status_code < 300
        }
        
        if headers:
            log_data['response_headers'] = dict(headers)
        
        if response_data and self.log_responses:
            if isinstance(response_data, dict):
                log_data['response_size'] = len(str(response_data))
                if len(str(response_data)) > 1000:
                    log_data['response_preview'] = str(response_data)[:500] + "...[truncated]"
                else:
                    log_data['response_data'] = response_data
            else:
                log_data['response_data'] = str(response_data)[:500]
        
        if error:
            log_data['error'] = {
                'type': type(error).__name__,
                'message': str(error)
            }
        
        level = logging.ERROR if error or status_code >= 400 else self.log_level
        self.logger.log(level, json.dumps(log_data, indent=2))
    
    def log_auth_event(self, api_name: str, auth_type: str, 
                      event: str, success: bool = True,
                      details: Optional[Dict] = None) -> None:
        """Log authentication events"""
        log_data = {
            'type': 'AUTH_EVENT',
            'api_name': api_name,
            'auth_type': auth_type,
            'event': event,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if details:
            filtered_details = self._filter_sensitive_data(details) if not self.log_sensitive_data else details
            log_data['details'] = filtered_details
        
        level = logging.WARNING if not success else logging.INFO
        self.logger.log(level, json.dumps(log_data, indent=2))
    
    def log_retry_attempt(self, api_name: str, endpoint: str, 
                         attempt: int, max_attempts: int,
                         delay: float, error: Exception) -> None:
        """Log retry attempts"""
        log_data = {
            'type': 'RETRY_ATTEMPT',
            'api_name': api_name,
            'endpoint': endpoint,
            'retry_attempt': attempt,
            'max_attempts': max_attempts,
            'delay_seconds': delay,
            'error': str(error),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.warning(json.dumps(log_data, indent=2))
    
    def _filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter sensitive data from logs"""
        sensitive_keys = {
            'authorization', 'auth', 'token', 'password', 'secret', 
            'key', 'apikey', 'api_key', 'bearer', 'basic'
        }
        
        filtered = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                filtered[key] = '[REDACTED]'
            else:
                filtered[key] = value
        
        return filtered
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"req_{int(time.time() * 1000000)}"
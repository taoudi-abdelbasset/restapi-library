# library: restapi_client Defaults
DEFAULT_CONFIG = {
    "timeout": 30,
    "raise_on_error": False,
    "retry": {
        "attempts": 1,
        "delay": 1.0,
        "backoff_factor": 2.0,
        "jitter": True
    },
    "auth_required": False,
    "body_required": False,
    # default version for API requests , can be change to V1 or 1 (depends)
    "default_version": "v1",
    "cache": {
        "type": "memory",
        "ttl": 3600  # 1 hour default
    },
    "logging": {
        "enabled": True,
        "level": "INFO",
        "log_requests": True,
        "log_responses": True,
        "log_sensitive_data": False
    }
}

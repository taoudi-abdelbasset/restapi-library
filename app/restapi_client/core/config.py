import json
from typing import Dict, Any, Optional
from pathlib import Path
from ..core.exceptions import ConfigurationError
from ..core.defaults import DEFAULT_CONFIG
from ..utils.env_parser import EnvParser

class ConfigParser:
    """Parse and validate API configuration with environment variable support"""
    
    def __init__(self, config_path: Optional[str] = None, 
                 config_dict: Optional[Dict] = None,
                 env_file: Optional[str] = '.env'):
        
        # Load environment variables
        if env_file:
            EnvParser.load_env_file(env_file)
        
        if config_path:
            self.config = self._load_from_file(config_path)
        elif config_dict:
            self.config = config_dict
        else:
            raise ConfigurationError("Either config_path or config_dict must be provided")
        
        # Parse environment variables in config
        self.config = EnvParser.parse_config(self.config)
        
        # Apply defaults
        self._apply_defaults()
        
        # Validate configuration
        self._validate_config()
    
    def _load_from_file(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
    
    def _apply_defaults(self) -> None:
        """Apply default configurations"""
        for api_name, api_config in self.config.items():
            # Apply API-level defaults
            for key, default_value in DEFAULT_CONFIG.items():
                if key not in api_config:
                    api_config[key] = default_value
            
            # Apply endpoint-level defaults
            if 'endpoints' in api_config:
                for version, endpoints in api_config['endpoints'].items():
                    for endpoint_name, endpoint_config in endpoints.items():
                        for key, default_value in DEFAULT_CONFIG.items():
                            if key not in endpoint_config and key in ['timeout', 'raise_on_error', 'retry', 'auth_required', 'body_required']:
                                endpoint_config[key] = default_value
    
    def _validate_config(self) -> None:
        """Validate configuration structure"""
        if not isinstance(self.config, dict):
            raise ConfigurationError("Configuration must be a dictionary")
        
        for api_name, api_config in self.config.items():
            self._validate_api_config(api_name, api_config)
    
    def _validate_api_config(self, api_name: str, api_config: Dict[str, Any]) -> None:
        """Validate individual API configuration"""
        required_fields = ['base_url', 'endpoints']
        
        for field in required_fields:
            if field not in api_config:
                raise ConfigurationError(f"Missing required field '{field}' in API '{api_name}'")
        
        if 'endpoints' in api_config:
            for version, endpoints in api_config['endpoints'].items():
                for endpoint_name, endpoint_config in endpoints.items():
                    self._validate_endpoint_config(api_name, endpoint_name, endpoint_config)
    
    def _validate_endpoint_config(self, api_name: str, endpoint_name: str, config: Dict[str, Any]) -> None:
        """Validate endpoint configuration"""
        required_fields = ['path', 'method']
        
        for field in required_fields:
            if field not in config:
                raise ConfigurationError(
                    f"Missing required field '{field}' in endpoint '{endpoint_name}' of API '{api_name}'"
                )
    
    def get_api_config(self, api_name: str) -> Dict[str, Any]:
        """Get configuration for specific API"""
        if api_name not in self.config:
            raise ConfigurationError(f"API '{api_name}' not found in configuration")
        return self.config[api_name]
    
    def get_endpoint_config(self, api_name: str, endpoint_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for specific endpoint"""
        api_config = self.get_api_config(api_name)
        
        if version is None:
            version = api_config.get('default_version', 'v1')
        
        if version not in api_config['endpoints']:
            raise ConfigurationError(f"Version '{version}' not found for API '{api_name}'")
        
        if endpoint_name not in api_config['endpoints'][version]:
            raise ConfigurationError(f"Endpoint '{endpoint_name}' not found in version '{version}' of API '{api_name}'")
        
        return api_config['endpoints'][version][endpoint_name]
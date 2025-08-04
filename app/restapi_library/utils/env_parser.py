
import os
import re
from typing import Any, Dict
from pathlib import Path

# library: restapi_client.utils.env_parser 
# This module provides functionality to parse environment variables in configuration JSON files.
class EnvParser:
    """Parse environment variables in configuration"""
    
    ENV_PATTERN = re.compile(r'\$\{([^}]+)\}')
    
    @classmethod
    def load_env_file(cls, env_path: str = '.env') -> None:
        """Load environment variables from .env file"""
        if not Path(env_path).exists():
            return
        
        with open(env_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"\'')
    
    @classmethod
    def parse_value(cls, value: Any) -> Any:
        """Parse environment variables in a value"""
        if not isinstance(value, str):
            return value
        
        def replace_env_var(match):
            env_var = match.group(1)
            # Support default values: ${VAR:default}
            if ':' in env_var:
                var_name, default_value = env_var.split(':', 1)
                return os.getenv(var_name, default_value)
            return os.getenv(env_var, match.group(0))
        
        return cls.ENV_PATTERN.sub(replace_env_var, value)
    
    @classmethod
    def parse_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively parse environment variables in configuration"""
        if isinstance(config, dict):
            return {key: cls.parse_config(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [cls.parse_config(item) for item in config]
        else:
            return cls.parse_value(config)